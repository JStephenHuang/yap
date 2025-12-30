class ThumbnailPromptConfig:
    """YouTube thumbnail prompt configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.5  # Slightly higher for creative punch

    VISUAL_STYLE: str = "dark atmospheric horror, cinematic, high contrast, dramatic lighting"

    SYSTEM_PROMPT: str = """You are a YouTube thumbnail designer for horror content.

Create ONE image generation prompt for a clickable thumbnail.

YOUTUBE THUMBNAIL RULES:
- Must work at SMALL SIZE (simple composition, high contrast, bold shapes)
- Creates curiosity/dread WITHOUT spoiling the story
- Single focal point (not busy/cluttered)
- Dramatic lighting and shadows
- NO text/words/letters (text is added separately in editing)
- NO clear faces (silhouettes, obscured, shadows)
- Should make viewer think "I need to know what happens"

STYLE: {visual_style}

Return ONLY a JSON object:
{{"thumbnail_prompt": "your prompt here"}}"""

    USER_PROMPT: str = """Story title: {title}

Story:
{story}

Generate 1 thumbnail prompt:"""

    USER_REVIEW_PROMPT: str = """Story title: {title}

Story: 
{story}

Your previous prompt:
{previous_output}

Feedback to address:
{feedback}

Revise the prompt based on the feedback."""


thumbnail_prompt_config = ThumbnailPromptConfig()
