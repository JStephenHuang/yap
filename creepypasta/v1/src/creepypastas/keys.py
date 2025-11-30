import torch
from pathlib import Path
from typing import List
from pydantic import Field
import pydantic_settings


class Keys(pydantic_settings.BaseSettings):
    """Application settings with defaults and validation."""

    # Where to save data
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    ASSETS_DIR: Path = PROJECT_ROOT / "assets"
    THREADS_PATH: Path = DATA_DIR / "threads"

    # Reddit Wrapper (PRAW)
    REDDIT_CLIENT_ID: str = Field(..., env="REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = Field(..., env="REDDIT_CLIENT_SECRET")

    # Triage settings
    MIN_WORDS: int = 500
    MAX_WORDS: int = 1500

    TRIAGE_LLM_MODEL: str = "llama3.1:8b"
    TRIAGE_LLM_PROMPT: str = """
    You are an expert horror editor specializing in creepypasta storytelling. 
    Your task is to evaluate whether the following unedited raw Reddit post 
    has strong potential to be adapted into an engaging, scary, and 
    fear-inducing creepypasta video for YouTube.

    ### Evaluation Criteria
    - **Engagement**: The text should be capable of capturing and holding attention.
    - **Horror Quality**: The text should contain elements of fear, dread, suspense, or unease.
    - **Creepypasta Fit**: The story should align with typical creepypasta themes 
    (e.g., urban legends, supernatural events, psychological horror).
    - **Potential**: Even if unpolished, the text should demonstrate 
    potential to be refined into an effective horror story.

    ### Instructions
    - Be concise and objective in your evaluation.
    - Do **not** rewrite or improve the story. Only judge its potential.
    - Always return a valid JSON object in the exact schema below.

    ### Schema
    {{
    "approved": true | false,
    "reasoning": "A short explanation of why it was approved or rejected."
    }}

    ### Story to Evaluate
    {story}
    """
    TRIAGE_LLM_TEMPERATURE: float = 0.0  # Make responses deterministic

    SANITIZER_LLM_MODEL: str = "llama3.1:8b"
    SANITIZER_LLM_TEMPERATURE: float = 0.3

    # Sanitizer Prompt
    SANITIZER_PROMPT: str = """
    You are an expert horror editor preparing creepypasta stories for audio narration. 
    Your task is to edit the following raw text so that it flows naturally when read aloud, 
    while preserving its original horror atmosphere.

    ### Editing Criteria
    - **Preserve Content**: Keep the original plot, tone, and writing style. Do not add or remove story elements.
    - **Improve Flow**: Correct grammar, punctuation, and awkward phrasing to ensure smooth narration.
    - **Clean Content**: Remove all meta-commentary (e.g., author's notes, Reddit references). Replace vulgarity with creepy alternatives when appropriate.
    - **Remove Stray Punctuation**: Eliminate unnecessary or standalone symbols (e.g., ".", "-", "*") on their own line.
    - **TTS Ready**: The final text must be plain, clean, and free of formatting artifacts that could disrupt Text-to-Speech.

    ### Instructions
    - Do not shorten the story significantly; preserve its length as much as possible.  
    - Do not include any commentary or explanation in your response.  
    - Always respond with a valid JSON object in the exact schema below.  

    ### Schema
    {{
    "sanitized_text": "The fully edited and cleaned story text."
    }}

    ### Story to Edit
    {story}
    """

    # YouTube Title Generation Prompt
    YOUTUBE_TITLE_PROMPT: str = """
    Your task is to create an engaging YouTube title for the following creepypasta story.

    ### Story Excerpt
    {story}

    ### Title Requirements
    - **Length**: Maximum 100 characters.  
    - **Tone**: Must be intriguing and scary, but not clickbait.  
    - **Focus**: Hint at the main threat/fear without giving away the ending.  
    - **Style**: Use power words that spark curiosity and fear.  
    - **Formatting**: Entirely in lowercase and end with "..." (exactly three dots).  
    - **Safety**: Title must be YouTube-friendly (no offensive content).  

    ### Examples
    - "the thing in my basement..."  
    - "i found something terrifying in my attic..."  
    - "the midnight visitor..."  

    ### Instructions
    - Generate only one title.  
    - Do not include explanations or extra text.  
    - Always respond with a valid JSON object in the exact schema below.  

    ### Schema
    {{
    "youtube_title": "the generated title here"
    }}
    """

    YOUTUBE_DESCRIPTION_PROMPT: str = """
    You are an expert YouTube copywriter specializing in horror content. 
    Your task is to create a short video description for the following creepypasta story.

    ### Story Sample
    ---
    {story}
    ---

    ### Requirements
    - **Length**: Exactly one sentence.  
    - **Tone**: Simple, creepy, and intriguing.  
    - **Formatting**: Entirely in lowercase.  
    - **Credit Line**: After the sentence, append a clear credit line in the format:  
    "credit: {author} | original thread: {thread_link}"  

    ### Instructions
    - Generate only one description.  
    - Do not include explanations or extra text.  
    - Always respond with a valid JSON object in the exact schema below.  

    ### Schema
    {{
    "youtube_description": "the generated description followed by the credit line"
    }}
    """
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
    {story}
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
