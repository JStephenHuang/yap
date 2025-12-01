from typing import Optional
from typing_extensions import TypedDict

from graph.types import TriageResult

class RedditThread(TypedDict):
    thread_id: str
    title: str
    content: str
    author: str
    url: str

class CreepypastaState(TypedDict):
    # Control flags
    enable_reviews: bool

    # Input
    reddit_thread: RedditThread

    # Run directory (runs/{thread_id}/)
    run_dir: str

    # Pipeline outputs
    triage: Optional[TriageResult]
    script: Optional[str]
    scene_prompts: Optional[list[str]]
    thumbnail_prompt: Optional[str]
    yt_title: Optional[str]
    yt_description: Optional[str]

    # Generated assets
    audio: Optional[str]
    scene_images: Optional[list[str]]
    thumbnail: Optional[str]
    video: Optional[str]
    youtube_link: Optional[str]

    # Review system
    current_feedback: Optional[str]
    checkpoint_thread_id: Optional[str]

    # Status tracking
    status: str
    message: Optional[str]