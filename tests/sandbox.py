from creepypastas.config import Settings
from creepypastas.services.reddit_scraper import RedditScrapper
from creepypastas.services.triage import Triage

import asyncio

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

    triage = Triage(
        csv_path=settings.THREADS_PATH / "reddit_threads_20250501_010038.csv",
        settings=settings,
    )

    response = asyncio.run(triage.triage())

    print(response)

    logger.info("Triage completed.")
