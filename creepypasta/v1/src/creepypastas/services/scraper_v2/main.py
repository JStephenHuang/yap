import praw
import praw.models
import praw.models.subreddits

import datetime
import pathlib
import typing
import pandas

from .llama3_1_8b import Llama3_1_8b
from .common import Scraper

from creepypastas.keys import Keys
from creepypastas.utils import ensure_dir

keys = Keys()

reddit_agent = "creepypasta-yap/0.1"
reddit = praw.Reddit(
    client_id=keys.REDDIT_CLIENT_ID,
    client_secret=keys.REDDIT_CLIENT_SECRET,
    user_agent=reddit_agent,
)

def scrape_threads(subreddits: list[str], limit) -> praw.models.Submission:
    all_threads = []

    for subreddit in subreddits:
        all_threads.extend(list(reddit.subreddit(subreddit).hot(limit=limit)))

    threads = [submission_to_dict(post) for post in all_threads]

    # Create dataframe
    data_frame = pandas.DataFrame(threads)

    # Generate timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reddit_threads_{timestamp}.csv"

    path = pathlib.Path(f"data/threads/{filename}")

    ensure_dir(path.parent)

    # Save to CSV
    data_frame.to_csv(path)

    return all_threads


def submission_to_dict(submission: praw.models.Submission) -> typing.Dict:

    return {
        "thread_id": submission.id,
        "title": submission.title,
        "raw_text": submission.selftext,
        "url": f"https://www.reddit.com{submission.permalink}",
        "author": str(submission.author),
    }


subreddits = ["CreepyPasta", "nosleep", "shortscarystories"]
limit = 5


def run():
    scraper = Scraper(Llama3_1_8b())

    threads = scrape_threads(subreddits, limit)


if __name__ == "__main__":
    scrape_threads(subreddits=subreddits, limit=limit)
