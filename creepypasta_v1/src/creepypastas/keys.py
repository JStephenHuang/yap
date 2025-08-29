from pydantic import Field
from pydantic_settings import BaseSettings


class Keys(BaseSettings):
    "All envs"

    # Reddit Wrapper (PRAW)
    REDDIT_CLIENT_ID: str = Field(..., env="REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = Field(..., env="REDDIT_CLIENT_SECRET")

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
    "youtube_title": "generated title here"
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

    YOUTUBE_DEFAULT_TAGS: list[str] = [
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
    YOUTUBE_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/youtube.upload",
    ]
    YOUTUBE_CLIENT_SECRET_FILE: str = Field(..., env="YOUTUBE_CLIENT_SECRET_FILE")
