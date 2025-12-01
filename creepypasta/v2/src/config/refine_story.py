class RefineStoryConfig:
    """Refine story node configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.7

    # Story refinement prompt
    SYSTEM_PROMPT: str = """You are rewriting a reddit creepypasta for text-to-speech narration.

CONTENT RULES:
- Remove meta commentary (edits, thank yous, "sorry for formatting", etc.)
- Cut fluff, keep only the story
- Keep it first-person and immersive
- Enhance atmosphere and suspense

TTS-FRIENDLY WRITING:
- Write conversationally. Use contractions (don't, it's, wasn't, couldn't)
- Keep sentences short and clear. Break long sentences into smaller ones.
- One idea per sentence. If a sentence has "and" or "but" connecting two complete thoughts, split it.

PUNCTUATION (CRITICAL):
Only use these four punctuation marks:
- Period (.) to end sentences
- Comma (,) for natural pauses within a sentence
- Question mark (?) for questions
- Exclamation mark (!) for emphasis

NEVER USE:
- Hyphens or dashes (no - or --)
- Ellipsis (no ...)
- Colons or semicolons (no : or ;)
- Parentheses (no ( ))
- Quotation marks for thoughts. Just write the thought directly.

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
