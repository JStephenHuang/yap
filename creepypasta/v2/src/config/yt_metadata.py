class YTMetadataConfig:
    """YouTube metadata generation configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.8  # Higher for creative titles

    SYSTEM_PROMPT: str = """[Write your system prompt here]

Define requirements for YouTube titles and descriptions. For example:
- Title requirements (length, hook format, keywords)?
- Description structure (teaser, context, hashtags)?
- SEO considerations?
- Output format (JSON)?"""

    USER_PROMPT: str = """[Write your user prompt template here]

Use {original_title}, {author}, {thread_url}, and {story_preview} placeholders.

For example:
Original title: {original_title}
Story preview: {story_preview}
Generate YouTube metadata:"""

    USER_REVIEW_PROMPT: str = """[Write your review prompt template here]

Use {original_title}, {author}, {thread_url}, {story_preview}, {previous_title}, {previous_description}, and {feedback} placeholders.

For example:
Original: {original_title}
Previous title: {previous_title}
Feedback: {feedback}
Revise:"""


yt_metadata_config = YTMetadataConfig()
