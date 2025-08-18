from creepypastas.config import Settings
from creepypastas.services.sanitizer import Sanitizer
from creepypastas.services.scraper import RedditScrapper
from creepypastas.services.triage import Triage

import asyncio

from creepypastas.services.tts import Narrator

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

    # logger.info("Scraping completed.")

    # triage = Triage(
    #     csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
    #     settings=settings,
    # )

    # response = asyncio.run(triage.triage())

    # sanitizer = Sanitizer(
    #     csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
    #     settings=settings,
    # )

    # asyncio.run(sanitizer.run())

    tts = Narrator(
        csv_path=settings.THREADS_PATH / "reddit_threads_20250818_004221.csv",
        settings=settings,
    )
    asyncio.run(tts.run())
