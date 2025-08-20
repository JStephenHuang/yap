import torch
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    """Application settings with defaults and validation."""

    # Where to save data
    DATA_DIR: Path = DATA_DIR
    THREADS_PATH: Path = DATA_DIR / "threads"

    # Reddit Wrapper (PRAW)
    REDDIT_CLIENT_ID: str = Field(..., env="REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = Field(..., env="REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = Field(default="creepypasta-yap/0.1")
    REDDIT_SUBREDDITS: List[str] = Field(
        default=["CreepyPasta", "nosleep", "shortscarystories"]
    )
    REDDIT_POST_LIMIT: int = Field(default=10)

    # Triage settings
    MIN_WORDS: int = 300
    MAX_WORDS: int = 2000

    TRIAGE_LLM_MODEL: str = "llama3.1:8b"
    TRIAGE_LLM_PROMPT: str = """
    You are an expert evaluator of creepypasta stories and experiences. Your task is to determine if the following raw text strictly adheres to the creepypasta theme, meaning it presents a genuinely scary story or a frightening personal experience.

    Consider the following criteria:
    - **Scary Theme:** The core of the text should revolve around creating fear, suspense, unease, or horror.
    - **Narrative or Experiential:** It should be presented as either a fictional story or a recounting of a personal (though potentially fictionalized) scary experience.
    - **Exclusion of Other Themes:** The text should *not* primarily focus on other genres or topics such as:
        - General fiction without a significant horror element.
        - Non-fiction accounts that are not inherently scary.
        - Discussions, analyses, or explanations of creepypasta or horror in general (meta-commentary).
        - Requests for information or help.
        - Advertisements or promotional material.
        - Content that is primarily humorous, satirical, or romantic.
        - Content that is excessively graphic or disturbing without a clear scary narrative purpose.

    Evaluate the following title and raw text:
    ---
    {title}
    {text}
    ---

    Based solely on the criteria above, determine if this text qualifies as a creepypasta (scary story or experience) and explain why the story eithers qualifies or does not.

    Respond with a JSON object in the following format:
    {{
      "approved": true/false,
      "reasoning": "explanation of why it was approved or rejected",
    }}
    """
    TRIAGE_LLM_TEMPERATURE: float = 0.0  # Make responses deterministic

    SANITIZER_LLM_MODEL: str = "llama3.1:8b"
    SANITIZER_LLM_TEMPERATURE: float = 0.0

    # New robust prompt template
    SANITIZER_LLM_TEMPERATURE: float = 0.3
    CONTENT_GENERATION_LLM_TEMPERATURE: float = 0.7

    # Sanitizer Prompt
    SANITIZER_PROMPT: str = """You are editing a creepypasta story for narration. Your goal is to make it flow better when read aloud while preserving the original style and atmosphere.
    Story:
    ---
    {story}
    ---

    Instructions:
    - Keep the exact same tone, vocabulary, and writing style as the original
    - Fix only awkward or broken phrasing so it flows naturally when read aloud
    - Remove or replace vulgar words with creepy but appropriate alternatives
    - Fix grammar and punctuation errors
    - Remove any meta-commentary or references to Reddit/posting
    - Do not add new plot points or change the story structure
    - Preserve all the original scares and atmosphere
    - Make sure dialogue feels natural when narrated

    Respond with a JSON object in the following format:
    {{
      "sanitized_text": "the improved story text",
    }}
    """

    # YouTube Title Generation Prompt
    YOUTUBE_TITLE_PROMPT: str = """Create an engaging YouTube title for this creepypasta story. The title should be clickable but not clickbait, and capture the essence of the horror.

    Story excerpt:
    ---
    {story_sample}
    ---

    Requirements:
    - Maximum 100 characters
    - Hint at the main threat/fear without spoiling it
    - Use power words that create intrigue
    - Make everything lower case and follow it everytime with ...
    - Make it YouTube-friendly (no offensive content)

    Examples of good titles:
    - "the thing in my basement..."
    - "i found something terrifying in my attic..."
    - "the midnight visitor..."

    Respond with a JSON object in the following format:
    {{
    "youtube_title": "scary but engaging title"
    }}
    """

    YOUTUBE_DESCRIPTION_PROMPT: str = """Create a short YouTube video description for this creepypasta story. 
    The description must be:
    - only one sentence
    - simple, creepy, and intriguing
    - all in lowercase
    - followed by a clear credit line with the author and the original thread link

    Story sample:
    ---
    {story_sample}
    ---

    Author: {author}
    Thread link: {thread_link}

    Respond with a JSON object in the following format:
    {{
    "youtube_description": "short description with credit"
    }}"""
    # Image Prompts Generation
    IMAGE_PROMPTS_GENERATION_PROMPT: str = """Create distinct image prompts for a creepypasta story. These will be used to generate atmospheric images during narration.

    Story context:
    ---
    {story}
    ---

    Create three different scene descriptions that capture key moments or atmospheres from the story. Each should be:
    - Visually distinct from the others
    - Atmospheric and creepy
    - Suitable for AI image generation
    - Focused on mood/setting rather than specific people
    - Forget about any text overlay
    - 1-2 sentences each

    Respond with a JSON object in the following format:
    {{
        "image_1_prompt": "first creepy image description",
        "image_2_prompt": "second creepy image description",
        "image_3_prompt": "third creepy image description"
    }}"""

    # Thumbnail Prompt Generation
    THUMBNAIL_PROMPT_GENERATION_PROMPT: str = """Create a YouTube thumbnail image prompt for this creepypasta story.

    Story sample:
    ---
    {story_sample}
    ---

    YouTube Title: {title}

    The thumbnail should:
    - Be eye-catching and creepy but not too graphic
    - It has to be dark, scary, eerie, and dark/red
    - Have high contrast for visibility
    - Capture the main theme/fear of the story
    - Be suitable for YouTube's guidelines
    - Have a cinematic, professional look
    - Forget about the text overlay

    Create ONE image prompt (1-2 sentences) that would generate an effective YouTube thumbnail. Focus on atmospheric horror elements, lighting, and composition that would make someone want to click.
    Respond with a JSON object in the following format:
    {{
    "thumbnail_prompt": "thumbnail description"
    }}"""

    TTS_OUTPUT_PATH: Path = DATA_DIR / "narrations"
    TTS_SPEAKER_PATH: Path = PROJECT_ROOT / "assets" / "speakers" / "oxley.mp3"

    # Image Generation Settings
    IMAGEGEN_HEIGHT: int = 1664
    IMAGEGEN_WIDTH: int = 928
    IMAGEGEN_MODEL: str = "stabilityai/stable-diffusion-xl-base-1.0"
    IMAGEGEN_TORCH_DTYPE: torch.dtype = torch.bfloat16
    IMAGEGEN_TORCH_DEVICE: str = "cuda"
    IMAGEGEN_OUTPUT_PATH: Path = DATA_DIR / "images"
    IMAGEGEN_GUIDANCE_SCALE: int = 9
    IMAGEGEN_INFERENCE_STEPS: int = 75

    GOOGLE_AI_STUDIO_KEY: str = Field(..., env="GOOGLE_AI_STUDIO_KEY")

    YOUTUBE_DEFAULT_TAGS: List[str] = [
        "creepypasta",
        "horror stories",
        "scary stories",
        "creepy narration",
        "true horror",
        "internet horror",
        "paranormal",
        "nightmare fuel",
        "scary pasta",
    ]
    YOUTUBE_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/youtube.upload",
    ]
    YOUTUBE_CLIENT_SECRET_FILE: str = Field(..., env="YOUTUBE_CLIENT_SECRET_FILE")

    class Config:
        """Pydantic config for environment variables."""

        env_file = ".env"
        env_file_encoding = "utf-8"
