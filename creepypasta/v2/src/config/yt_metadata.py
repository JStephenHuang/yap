class YTMetadataConfig:
    """YouTube metadata generation configuration"""

    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.8  # Higher for creative titles

    SYSTEM_PROMPT: str = """You are a YouTube SEO expert for horror/creepypasta content.

Generate a title and description that maximize clicks while staying true to the story.

TITLE RULES:
- Max 60 characters (YouTube truncates after ~60)
- Hook formats that work: "I Found...", "My [X] Started...", "Don't Read This At Night", "True Story"
- Include tension words: disturbing, terrifying, unexplained, true, found
- NO clickbait that misrepresents the actual story
- NO emojis in title
- NO ALL CAPS (except one word for emphasis max)

DESCRIPTION RULES:
- First 2 lines are visible in search - make them a hook/teaser
- Line 3+: brief story context (1-2 sentences)
- Include credit line: "Original story from Reddit: [will be added]"
- End with hashtags on own line: #creepypasta #horror #scary #truescary #nosleep
- Total: 200-400 characters

Return JSON:
{{"yt_title": "your title", "yt_description": "your description"}}"""

    USER_PROMPT: str = """Original Reddit title: {original_title}

Author: {author}
Thread: {thread_url}

Story (first 800 chars):
{story_preview}

Generate YouTube title and description:"""

    USER_REVIEW_PROMPT: str = """Original Reddit title: {original_title}

Author: {author}
Thread: {thread_url}

Story (first 800 chars):
{story_preview}

Your previous title: {previous_title}
Your previous description: {previous_description}

Feedback to address:
{feedback}

Revise based on the feedback."""


yt_metadata_config = YTMetadataConfig()
