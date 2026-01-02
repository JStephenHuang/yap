class TriageConfig():
    """Triage node configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.0


    # Triage evaluation prompt
    # TODO: Customize these prompts to define how you want to evaluate Reddit posts for video potential
    SYSTEM_PROMPT: str = """# Role
You are a content strategist for a horror narration channel on YouTube.

# Objective
Evaluate Reddit creepypasta posts to determine their suitability for adaptation into engaging video narrations.

# Evaluation Rubric
- **The Hook:** Does the first paragraph establish a unique, unsettling mystery or a "wrong" normalcy?
- **Pacing:** Is there a gradual escalation of "The Uncanny" rather than a sudden jump-scare?
- **Ear-Feel:** Is it written in a natural, first-person "confessional" style?.
- **The Unresolved:** Does the ending leave a lingering, "could happen to you" dread rather than a neat explanation?

# Criteria Rules
- For each evaluation, provide your decision with a one-sentence reason."""

    USER_PROMPT: str = """Evaluate the following Reddit creepypasta post:

**Thread Title:** {title}
**Full Story Text:** {text}"""


# Import this directly: from config.triage import triage_config
triage_config = TriageConfig()
