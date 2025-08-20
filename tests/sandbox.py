from creepypastas.config import Settings
from creepypastas.services.imagegen import ImageGen
from creepypastas.services.sanitizer import Sanitizer
from creepypastas.services.scraper import RedditScrapper
from creepypastas.services.triage import Triage
from creepypastas.services.ffmpeg import Ffmpeg

import asyncio

from creepypastas.services.tts import Narrator
from creepypastas.services.ytapi import YouTubeAPI

settings = Settings()

import logging


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,  # minimum level to show
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run():
    """Run the Reddit scraper."""
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting sandbox...")

    # reddit_scraper = RedditScrapper(settings)
    # reddit_scraper.scrape_stories()

    # triage = Triage(
    #     csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
    #     settings=settings,
    # )

    # asyncio.run(triage.triage())

    # sanitizer = Sanitizer(
    #     csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
    #     settings=settings,
    #     thread_id="1mt62jp",
    # )

    # sanitizer.run()

    # tts = Narrator(
    #     csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
    #     settings=settings,
    #     rerun=True,
    # )
    # asyncio.run(tts.run())

    # imagegen = ImageGen(
    #     csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
    #     settings=settings,
    #     thread_id="1mt62jp",
    # )

    # asyncio.run(imagegen.run())

    ffmpeg = Ffmpeg(
        csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
        settings=settings,
        thread_id="1mt62jp",
    )

    ffmpeg.run()

    # ytapi = YouTubeAPI(
    #     csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
    #     settings=settings,
    #     thread_id="1mt62jp",
    # )

    # ytapi.run()
