class RefineStoryConfig:
    """Refine story node configuration"""

    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.7

    # Story refinement prompt
    SYSTEM_PROMPT: str = """You are rewriting a reddit creepypasta for professional narration.

Your job:
- Remove meta commentary (edits, thank yous, "sorry for formatting", etc.)
- Cut fluff and keep only the story
- Rewrite for smooth audio flow (natural pacing, no awkward phrasing)
- Enhance atmosphere and suspense
- Keep it first-person and immersive

Return ONLY the refined story. No preamble."""

    USER_PROMPT: str = """Original post:

{content}

Rewrite this for narration:"""

    USER_REVIEW_PROMPT: str = """Original post:

{content}

Your previous version:

{previous_output}

Feedback to address:
{feedback}

Revise ONLY the parts mentioned in the feedback. Keep everything else unchanged."""


refine_story_config = RefineStoryConfig()
