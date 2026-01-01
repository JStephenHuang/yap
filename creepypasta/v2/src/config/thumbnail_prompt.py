class ThumbnailPromptConfig:
    """YouTube thumbnail prompt configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.5  # Slightly higher for creative punch

    VISUAL_STYLE: str = "dark atmospheric horror, cinematic, high contrast, dramatic lighting"

    SYSTEM_PROMPT: str = """[Write your system prompt here]

Define how to create thumbnail image prompts. For example:
- YouTube thumbnail requirements (creepy, dramatic, single focal point)?
- What to avoid (text, faces, spoilers)?
- Visual style?
- Output format (JSON, plain text)?

Use {visual_style} placeholder if needed."""

    USER_PROMPT: str = """[Write your user prompt template here]

Use {title} and {story} placeholders.

For example:
Title: {title}
Story: {story}
Generate thumbnail prompt:"""

    USER_REVIEW_PROMPT: str = """[Write your review prompt template here]

Use {title}, {story}, {previous_output}, and {feedback} placeholders.

For example:
Title: {title}
Previous: {previous_output}
Feedback: {feedback}
Revise:"""


thumbnail_prompt_config = ThumbnailPromptConfig()
