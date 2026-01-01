class TriageConfig():
    """Triage node configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.0


    # Triage evaluation prompt
    # TODO: Customize these prompts to define how you want to evaluate Reddit posts for video potential
    SYSTEM_PROMPT: str = """[Write your system prompt here]
    
Define the criteria for evaluating stories. For example:
- What makes a good story for your channel?
- What metrics matter (hook, tension, structure, viral potential)?
- How should the LLM evaluate and respond?"""

    USER_PROMPT: str = """[Write your user prompt template here]

Use these placeholders: {title}, {text}, {score}, {upvote_ratio}

For example:
Title: {title}
Story: {text}
Evaluate this post."""


# Import this directly: from config.triage import triage_config
triage_config = TriageConfig()
