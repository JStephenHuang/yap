from pathlib import Path
import logging

import ffmpeg
import pandas as pd

from creepypastas.config import Settings
from creepypastas.utils import find_thread, save

logger = logging.getLogger(__name__)


class Ffmpeg:
    def __init__(
        self,
        csv_path: Path,
        settings: Settings,
        thread_id: str | None = None,
        update: bool = False,
    ):
        self.csv_path = csv_path
        self.settings = settings
        self.df = pd.read_csv(csv_path)
        self.thread_id = thread_id
        self.update = update

    def _get_paths_for_thread(self, row: pd.Series) -> tuple[list[str], str]:
        """Return image paths and audio path for a given thread_id."""
        image_paths = []

        for i in range(1, 4):
            image_path = row.get(f"image_{i}_path")

            if image_path is None:
                raise Exception(f"Image path {i} is None")

            image_paths.append(str(image_path))

        audio_path = row.get("audio_path")

        if audio_path is None:
            raise Exception("Audio path is None")

        return image_paths, str(audio_path)

    def _merge_media(
        self,
        thread_id: str,
        output_dir: Path,
        image_paths: list[str],
        audio_path: str,
    ) -> str:

        video_output_path = output_dir / "final_video.mp4"
        video_output_path_exists = video_output_path.exists()

        if video_output_path_exists and not self.update:
            logger.info(f"Video already exists for thread {thread_id}, skipping.")
            return

        logger.info(
            f"{'Updating' if self.update and video_output_path_exists else 'Generating'} video for thread {thread_id}..."
        )

        fade_duration = 1.5  # seconds
        black_duration = 2  # seconds
        width, height = 1280, 720
        framerate = 30
        pix_fmt = "yuv420p"

        # Black intro/outro
        black_intro = ffmpeg.input(
            f"color=black:s={width}x{height}:d={black_duration}:r={framerate}",
            f="lavfi",
        )
        black_outro = ffmpeg.input(
            f"color=black:s={width}x{height}:d={black_duration}:r={framerate}",
            f="lavfi",
        )

        # Get audio duration
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe["format"]["duration"])

        image_duration = audio_duration / len(image_paths)

        # Prepare image streams with scale, pad, setsar, fade in/out
        image_streams = []
        for path in image_paths:
            stream = ffmpeg.input(path, loop=1, t=image_duration, framerate=framerate)
            stream = stream.filter(
                "scale", w=width, h=height, force_original_aspect_ratio="increase"
            )
            stream = stream.filter("crop", w=width, h=height)
            stream = stream.filter("setsar", sar=1)
            stream = stream.filter(
                "fade", type="in", start_time=0, duration=fade_duration
            )
            stream = stream.filter(
                "fade",
                type="out",
                start_time=image_duration - fade_duration,
                duration=fade_duration,
            )
            image_streams.append(stream)

        # Concatenate intro + images + outro
        concat_streams = [black_intro] + image_streams + [black_outro]
        video_stream = ffmpeg.concat(*concat_streams, v=1, a=0).node
        video = video_stream[0]
        video = video.filter("format", pix_fmt)  # Apply format after concat

        # Add audio
        audio = ffmpeg.input(audio_path)

        ffmpeg.output(
            video,
            audio,
            str(video_output_path),
            vcodec="h264_nvenc",
            acodec="aac",
            pix_fmt=pix_fmt,
            shortest=None,
        ).run(overwrite_output=True)

        return str(video_output_path)

    def _process_thread(self, row: pd.Series, idx: int, thread_id: str) -> None:
        status = row.get("status")
        image_populated = bool(row.get("image_populated"))

        if not image_populated or status == "rejected":
            logger.warning(
                f"Thread {thread_id}'s status: {status}, image_populated: {image_populated}, skipping."
            )
            return

        output_dir = self.settings.DATA_DIR / thread_id
        logger.info(f"pegging thread {thread_id}...")

        image_paths, audio_path = self._get_paths_for_thread(row)

        video_output_path = self._merge_media(
            idx, thread_id, output_dir, image_paths, audio_path
        )

        self.df.at[idx, "status"] = "video_populated"  # this could cause errors...
        self.df.at[idx, "video_path"] = video_output_path

        save(self.csv_path, self.df)
        logger.info(f"Video saved for thread {thread_id}: {video_output_path}")

    def run(self) -> None:
        try:
            if self.thread_id:
                # Process only the specified thread_id
                row, idx = find_thread(self.thread_id, self.df)

                self._process_thread(row, idx, self.thread_id)

                return

            # Process all eligible threads
            for idx, row in self.df.iterrows():
                thread_id = row.get("thread_id")

                self._process_thread(row, idx, thread_id)

        except ffmpeg.Error as e:
            logger.error(f"ffmpeg error for thread {thread_id}: {e}")
        except Exception as e:
            logger.error(f"Error for thread {thread_id}: {e}")
