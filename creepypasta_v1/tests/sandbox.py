from creepypastas.keys import Keys
from creepypastas.services.ffmpeg import Ffmpeg
from creepypastas.services.imagegen import ImageGen
from creepypastas.services.sanitizer import Sanitizer
from creepypastas.services.scraper import RedditScrapper
from creepypastas.services.triage import Triage
from creepypastas.services.tts import Narrator
from creepypastas.services.ytapi import YouTubeAPI

settings = Keys()

import logging


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,  # minimum level to show
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )


def run():
    """Run the Reddit scraper."""
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting sandbox...")

    thread_id = "1mxe8r5"
    # csv_path = settings.THREADS_PATH / "reddit_threads_20250818_004221.csv"
    csv_path = settings.THREADS_PATH / "reddit_threads_20250823_040539.csv"

    # reddit_scraper = RedditScrapper(settings)
    triage = Triage(
        csv_path=csv_path,
        settings=settings,
    )
    # sanitizer = Sanitizer(
    #     csv_path=csv_path,
    #     settings=settings,
    #     thread_id=thread_id,
    # )
    # tts = Narrator(
    #     csv_path=csv_path,
    #     settings=settings,
    #     thread_id=thread_id,
    # )
    # imagegen = ImageGen(
    #     csv_path=csv_path,
    #     settings=settings,
    #     thread_id=thread_id,
    # )
    # ffmpeg = Ffmpeg(
    #     csv_path=csv_path,
    #     settings=settings,
    #     thread_id=thread_id,
    # )
    # ytapi = YouTubeAPI(
    #     csv_path=csv_path,
    #     settings=settings,
    #     thread_id=thread_id,
    # )

    while True:
        cmd = input("Enter a command (or 'exit' to quit): ")
        if cmd == "exit":
            break

        if cmd == "scrape":
            reddit_scraper = RedditScrapper(settings)
            reddit_scraper.scrape_stories()

        if cmd == "triage":

            triage.triage()

        if cmd == "get_approved":

            print(triage.get_approved_thread())

        if cmd == "sanitize":
            sanitizer = Sanitizer(
                csv_path=csv_path,
                settings=settings,
                thread_id=thread_id,
            )

            sanitizer.run()

        if cmd == "tts":
            # tts = Narrator(story_path="story1/sanitized_text.txt")
            tts = Narrator(
                csv_path=csv_path,
                settings=settings,
                thread_id=thread_id,
            )
            tts.run()

        if cmd == "imagegen":
            imagegen = ImageGen(
                csv_path=csv_path,
                settings=settings,
                thread_id=thread_id,
                # update=True,
            )

            imagegen.run()

        if cmd == "ffmpeg":
            ffmpeg = Ffmpeg(
                csv_path=csv_path,
                settings=settings,
                thread_id=thread_id,
                update=True,
            )

            ffmpeg.run()

        if cmd == "ytapi":
            ytapi = YouTubeAPI(
                csv_path=csv_path,
                settings=settings,
                thread_id=thread_id,
            )

            ytapi.run()

        if cmd == "change_thread":
            thread_id = str(input("Enter new thread ID: "))

        if cmd == "change_csv":
            csv_path = str(input("Enter new CSV path: "))
