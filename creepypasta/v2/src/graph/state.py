from typing import Optional
from typing_extensions import TypedDict

class RedditThread(TypedDict):
    id: str
    title: str
    author: str
    content: str

class CreepypastaState(TypedDict):
    reddit_thread: Optional[RedditThread]
    
    yt_title: Optional[str]
    yt_description: Optional[str]
    
    story_body: Optional[str]
    narration_prompt: Optional[str]
    audio: Optional[str]

    images_prompt: Optional[str]
    images: Optional[list[str]]
    
    thumbnail_prompt: Optional[str]
    thumbnail: Optional[str]
    
    status: str
    message: Optional[str]