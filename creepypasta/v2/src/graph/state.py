from typing import Optional
from typing_extensions import TypedDict

from infrastructure.database import RedditThreadRow

from services.triage import TriageResult

class RedditThread(TypedDict):
    thread_id: str
    title: str
    content: str
    author: str
    url: str

class CreepypastaState(TypedDict):
    reddit_thread: RedditThread
    
    triage: Optional[TriageResult]
    
    yt_title: Optional[str]
    yt_description: Optional[str]
    
    story_body: Optional[str]
    audio: Optional[str]

    images_prompt: Optional[str]
    images: Optional[list[str]]
    
    thumbnail_prompt: Optional[str]
    thumbnail: Optional[str]
    
    status: str
    message: Optional[str]