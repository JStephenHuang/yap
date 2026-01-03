class YTMetadataConfig:
    """YouTube metadata generation configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.8  # Higher for creative titles

    SYSTEM_PROMPT: str = """# Role
You are a YouTube content strategist for a horror narration channel.

# Objective
Generate a intriguing and curious striking YouTube title and description for a horror narration video based on the provided Reddit creepypasta story details.

# Guidelines
- Keep the title and description strictly lowercase
- Title: Focus on curiosity and intrigue to maximize click-through rate.
- Description: Provide a brief summary of the story in 1-2 sentences, then the original Reddit thread link and the hashtags: #creepypasta #horror #scary #truescary #nosleep.

# Examples

## Titles:
- "when my family forget that to tell me about our attic..."
- "a dark figure passed my neighbourhood, my friend said not to look at him...".

## Descriptions:
a mysterious woman changed my life. i was homeless, but she gave me hope. original story from reddit: https://reddit.com/r/nosleep/comments/1pwunqf/an_angel_died_in_the_alleyway/ #creepypasta #horror #scary #truescary #nosleep"""

    USER_PROMPT: str = """Generate YouTube metadata for the following Reddit creepypasta story:

**Thread Title:** {original_title}
**Author:** {author}
**Thread URL:** {thread_url}
**Story Preview:** {story_preview}"""

    USER_REVIEW_PROMPT: str = """Review and revise the YouTube metadata SOLELY based on the user's feedback:

**Thread Title:** {original_title}
**Author:** {author}
**Thread URL:** {thread_url}
**Story Preview:** {story_preview}

# Previous Metadata
Youtube Title: {previous_title}
Youtube Description: {previous_description}

# User Feedback
{feedback}"""


yt_metadata_config = YTMetadataConfig()
