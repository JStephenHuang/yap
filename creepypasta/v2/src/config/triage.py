class TriageConfig():
    """Triage node configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.0


    # Triage evaluation prompt
    SYSTEM_PROMPT: str = """You are evaluating reddit posts for creepypasta video potential.

A good creepypasta has:
- Compelling hook in the first few sentences
- Atmospheric tension and dread
- Clear narrative structure
- Viral potential for YouTube

Evaluate the post and provide your decision with a one-sentence reason."""

    USER_PROMPT: str = """Title: {title}

Story:
{text}

Score: {score} | Upvote Ratio: {upvote_ratio}"""


# Import this directly: from config.triage import triage_config
triage_config = TriageConfig()
