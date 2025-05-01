from typing_extensions import TypedDict, List, Optional


class StoryState(TypedDict):
    # Reddit thread identifiers & raw content
    thread_id: str
    raw_text: str

    # Sanitized & paraphrased story ready for narration
    sanitized_text: str

    # YouTube metadata
    youtube_title: str
    youtube_description: str

    # Image generation prompts & resulting asset paths
    image_prompts: List[str]  # e.g. three scene prompts
    thumbnail_prompt: str
    image_paths: List[str]  # filepaths to generated images
    thumbnail_path: Optional[str]

    # Narration output
    audio_path: Optional[str]  # filepath to the TTS audio file

    # Pipeline status flags
    used_for_video: bool  # already published?
    errors: Optional[List[str]]  # any errors encountered
