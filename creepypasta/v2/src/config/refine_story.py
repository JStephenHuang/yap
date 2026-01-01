class RefineStoryConfig:
    """Refine story node configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.3

    # Story refinement prompt
    # TODO: Customize these prompts to define how you want to refine Reddit stories for narration
    SYSTEM_PROMPT: str = """[Write your system prompt here]
    
Define rules for story refinement. For example:
- How to adapt Reddit posts for TTS (remove meta commentary, fix grammar)?
- Writing style (conversational, formal, immersive)?
- Punctuation rules for natural speech?
- Length requirements?"""

    USER_PROMPT: str = """[Write your user prompt template here]

Use {content} placeholder for the original text.

For example:
Original post:
{content}

Rewrite for narration."""

    USER_REVIEW_PROMPT: str = """[Write your review prompt template here]

Use {content}, {previous_output}, and {feedback} placeholders.

For example:
Original: {content}
Previous: {previous_output}
Feedback: {feedback}
Revise:"""

refine_story_config = RefineStoryConfig()
