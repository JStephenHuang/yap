import torch
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with defaults and validation."""

    # Where to save data
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    ASSETS_DIR: Path = PROJECT_ROOT / "assets"
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
    MIN_WORDS: int = 500
    MAX_WORDS: int = 1500

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
    SANITIZER_PROMPT: str = """You are an editor preparing a creepypasta for audio narration. Your task is to polish the provided story to ensure it flows perfectly when read aloud, while preserving its original horror.
    Story:
    ---
    {story}
    ---

    Editing Guidelines:
    1.  **Preserve the Core:** Maintain the original tone, writing style, and plot. Do not add or remove story elements.
    2.  **Enhance Flow:** Correct grammar, punctuation, and awkward phrasing to ensure a smooth, natural narration.
    3.  **Clean Content:** Replace vulgarity with thematically creepy alternatives and remove all meta-commentary (e.g., author's notes, Reddit references).
    4.  **Format for TTS:** The final text must be clean of any formatting artifacts that would disrupt a Text-to-Speech engine. Specifically, ensure there are no single punctuation marks (like periods, hyphens, or asterisks) left on their own lines.

    Respond ONLY with a JSON object in the following format, with no other text before or after it:
    {
    "sanitized_text": "The fully edited and cleaned story text goes here."
    }
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
    - Make everything lowercase and follow it everytime with ...
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
    IMAGE_PROMPTS_GENERATION_PROMPT: str = """Read the following creepypasta story and produce three prompts to generate three scene images for the visual of the creepypasta. 
   
    Story context:
    ---
    {story}
    ---

    Each prompt for the image generation should:
    - Photorealistic or surrealistic
    - Each scene should capture a distinct key moment or atmosphere from the story. 
    - They must be vividly described in 1-2 sentences, focusing on setting, lighting, and mood. 
    - Emphasize ominous, sad, dark, and mysterious environments that feel unsettling and chilling. 
    - Try to keep a red lighting and dark shadows atmosphere.

    Respond with a JSON object in the following format:
    {{
        "image_1_prompt": "first creepy image description",
        "image_2_prompt": "second creepy image description",
        "image_3_prompt": "third creepy image description"
    }}"""

    # Thumbnail Prompt Generation
    THUMBNAIL_PROMPT_GENERATION_PROMPT: str = """
    Create a YouTube thumbnail image prompt for this creepypasta story.

    Story sample:
    ---
    {story_sample}
    ---

    YouTube Title: {title}

    The thumbnail should:
    - Be eye-catching and creepy but not too graphic
    - Use dark red/black tones for atmosphere
    - Have high contrast for visibility
    - Capture the main theme or fear of the story
    - Be suitable for YouTube guidelines
    - Look cinematic and professional
    {{
    "thumbnail_prompt": "One cinematic, photorealistic or surrealism scene description in 1-2 sentences, inspired by the story, emphasizing eerie atmosphere, dramatic lighting, and ominous mood."
    }}"""

    TTS_OUTPUT_PATH: Path = DATA_DIR / "narrations"
    TTS_SPEAKER_PATH: Path = ASSETS_DIR / "speakers" / "ghoul.mp3"

    # Image Generation Settings
    IMAGEGEN_WIDTH: int = 1280
    IMAGEGEN_HEIGHT: int = 720
    IMAGEGEN_MODEL: str = "RunDiffusion/Juggernaut-XI-v11"
    IMAGEGEN_URL: str = (
        "https://huggingface.co/RunDiffusion/Juggernaut-XI-v11/resolve/main/Juggernaut-XI-byRunDiffusion.safetensors"
    )
    IMAGEGEN_TORCH_DTYPE: torch.dtype = torch.float16
    IMAGEGEN_TORCH_DEVICE: str = "cuda"
    IMAGEGEN_OUTPUT_PATH: Path = DATA_DIR / "images"
    IMAGEGEN_GUIDANCE_SCALE: int = 2
    IMAGEGEN_INFERENCE_STEPS: int = 10

    HF_TOKEN: str = Field(..., env="HF_TOKEN")

    GOOGLE_AI_STUDIO_KEY: str = Field(..., env="GOOGLE_AI_STUDIO_KEY")
    GOOGLE_IMAGEGEN_MODEL: str = "imagen-4.0-generate-001"

    FFMPEG_FONT: Path = ASSETS_DIR / "fonts" / "FoulFiend.ttf"

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
    YOUTUBE_CHANNEL_ID: str = Field(..., env="YOUTUBE_CHANNEL_ID")

    class Config:
        """Pydantic config for environment variables."""

        env_file = ".env"
        env_file_encoding = "utf-8"
