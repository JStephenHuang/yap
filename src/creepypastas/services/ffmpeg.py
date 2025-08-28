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
        title: str,
        credit: str,
    ) -> str:

        video_output_path = output_dir / "final_video.mp4"
        video_output_path_exists = video_output_path.exists()

        if video_output_path_exists and not self.update:
            logger.info(f"Video already exists for thread {thread_id}, skipping.")
            return

        logger.info(
            f"{'Updating' if self.update and video_output_path_exists else 'Generating'} video for thread {thread_id}..."
        )

        fade_duration = 2
        intro_duration = 5
        width, height = 1280, 720
        framerate = 25
        pix_fmt = "yuv420p"
        font_path = str(self.settings.FFMPEG_FONT)

        probe = ffmpeg.probe(audio_path)

        audio_duration = float(probe["format"]["duration"])
        image_duration = audio_duration / len(image_paths)

        print(f"Audio duration: {audio_duration}, Image duration: {image_duration}")

        intro = (
            ffmpeg.input(
                f"color=c=black:s={width}x{height}:r={framerate}:d={intro_duration}",
                f="lavfi",
            )
            .filter(
                "drawtext",
                fontfile=font_path,
                text=title,
                fontcolor="white",
                fontsize=32,
                x="(w-text_w)/2",
                y="(h-text_h)/2",
                enable="between(t,0.5,4)",
            )
            .filter(
                "drawtext",
                fontfile=font_path,
                text=credit,
                fontcolor="white",
                fontsize=16,
                x="(w-text_w)/2",
                y="(h-text_h)/2 + 64",
                enable="between(t,0.5,4)",
            )
            .filter("scale", w=width, h=height, force_original_aspect_ratio="increase")
            .filter("format", pix_fmt)
        )

        image_streams = []
        for i, path in enumerate(image_paths):
            stream = ffmpeg.input(
                path,
                loop=1,
                t=image_duration,
                framerate=framerate,
                ss=(i * image_duration),
            )

            stream = stream.filter(
                "scale", w=width, h=height, force_original_aspect_ratio="increase"
            )

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

        video = ffmpeg.concat(intro, *image_streams, v=1, a=0).node
        audio = ffmpeg.input(audio_path)
        audio = audio.filter("adelay", delays=f"{intro_duration}s", all=True)

        ffmpeg.output(
            video[0],
            audio,
            str(video_output_path),
            vcodec="hevc_nvenc",
            acodec="aac",
            pix_fmt=pix_fmt,
            r=framerate,
            shortest=None,
        ).run(overwrite_output=True)

        return str(video_output_path)

    def _process_thread(self, row: pd.Series, idx: int, thread_id: str) -> None:
        status = row.get("status")
        image_populated = bool(row.get("image_populated"))
        narrated = bool(row.get("narrated"))

        if not image_populated or status == "rejected" or not narrated:
            logger.warning(
                f"Thread {thread_id}'s status: {status}, image_populated: {image_populated}, narrated: {narrated}, skipping."
            )
            return

        output_dir = self.settings.DATA_DIR / thread_id
        logger.info(f"pegging thread {thread_id}...")

        image_paths, audio_path = self._get_paths_for_thread(row)
        title = row.get("youtube_title")
        credit = row.get("author")

        video_output_path = self._merge_media(
            thread_id, output_dir, image_paths, audio_path, title, credit
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
            logger.error(f"ffmpeg error for thread: {e}")
        except Exception as e:
            logger.error(f"Error for thread: {e}")


if __name__ == "__main__":
    from creepypastas.config import Settings

    settings = Settings()
    csv_path = settings.THREADS_PATH / "reddit_threads_20250823_040539.csv"
    thread_id = "1mxe8r5"
    ffmpeg_service = Ffmpeg(csv_path=csv_path, settings=settings, thread_id=thread_id)
    ffmpeg_service.run()
