from pathlib import Path
import logging

import ffmpeg
import pandas as pd

from creepypastas.config import Settings


class Ffmpeg:
    def __init__(
        self,
        csv_path: Path,
        settings: Settings,
        thread_id: str | None = None,
    ):
        self.csv_path = csv_path
        self.settings = settings
        self.df = pd.read_csv(csv_path)
        self.thread_id = thread_id

    def _get_paths_for_thread(
        self, thread_id: str
    ) -> tuple[list[str] | None, str | None]:
        """Return image paths and audio path for a given thread_id."""
        row = self.df.loc[self.df["thread_id"] == thread_id]

        row = row.iloc[0]  # get first match

        image_paths = []

        for i in range(1, 4):
            image_path = row.get(f"image_{i}_path")

            if image_path == None:
                raise Exception(f"Image path {i} none")

            image_paths.append(str(Path(image_path).resolve()))

        audio_path = row.get("audio_path")

        # Filter out missing image paths
        image_paths = [
            str(Path(p).resolve()) for p in image_paths if p and Path(p).exists()
        ]

        if audio_path:
            audio_path = str(Path(audio_path).resolve())
        else:
            audio_path = None

        return image_paths, audio_path

    def _merge_media(
        self,
        thread_id: str,
        output_dir: Path,
        image_paths: list[str],
        audio_path: str,
    ) -> None:
        if not image_paths or not audio_path or not Path(audio_path).exists():
            raise Exception(f"Missing media for thread {thread_id}, skipping.")

        if len(image_paths) == 0:
            raise Exception(f"Missing media for thread {thread_id}, skipping.")

        fade_duration = 2  # seconds
        black_duration = 1  # seconds
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
        output_video = output_dir / "final_video.mp4"

        ffmpeg.output(
            video,
            audio,
            str(output_video),
            vcodec="h264_nvenc",
            acodec="aac",
            pix_fmt=pix_fmt,
            shortest=None,
        ).run(overwrite_output=True)

        self.csv_path
        logging.info(f"Video created for thread {thread_id}: {output_video}")

    def run(self) -> None:
        try:
            if self.thread_id:
                # Process only the specified thread_id
                row = self.df.loc[self.df["thread_id"] == self.thread_id]
                if row.empty:
                    logging.warning(f"No row found for thread {self.thread_id}")
                    return
                row = row.iloc[0]
                if bool(row.get("image_populated")) and (
                    row.get("status") != "rejected"
                ):
                    output_dir = self.settings.DATA_DIR / self.thread_id
                    logging.info(f"pegging thread {self.thread_id}...")
                    image_paths, audio_path = self._get_paths_for_thread(self.thread_id)
                    self._merge_media(
                        self.thread_id, output_dir, image_paths, audio_path
                    )

                return

            # Process all eligible threads
            for idx, row in self.df.iterrows():
                thread_id = row.get("thread_id", f"thread_{idx}")
                if row.get("status") == "image_populated" and bool(
                    row.get("image_populated")
                ):
                    output_dir = self.settings.DATA_DIR / thread_id
                    logging.info(f"pegging thread {thread_id}...")
                    image_paths, audio_path = self._get_paths_for_thread(thread_id)
                    self._merge_media(thread_id, output_dir, image_paths, audio_path)

        except ffmpeg.Error as e:
            logging.error(f"ffmpeg error for thread {thread_id}: {e}")
        except Exception as e:
            logging.error(f"Error for thread {thread_id}: {e}")
