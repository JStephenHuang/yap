class ScenePromptsConfig:
    """Scene prompts generation configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.5

    # Fixed number of scenes
    NUM_SCENES: int = 3

    # Visual style applied to all prompts
    VISUAL_STYLE: str = "dark atmospheric horror, cinematic lighting"

    SYSTEM_PROMPT: str = """[Write your system prompt here]

Define how to create image generation prompts. For example:
- How many scenes? What moments to capture?
- Visual style (horror, cinematic, etc.)?
- What to avoid (text, faces, gore)?
- Prompt structure and length?

Use {num_scenes} and {visual_style} placeholders if needed."""

    USER_PROMPT: str = """[Write your user prompt template here]

Use {story} and {num_scenes} placeholders.

For example:
Story:
{story}

Generate {num_scenes} scene prompts:"""

    USER_REVIEW_PROMPT: str = """[Write your review prompt template here]

Use {story}, {previous_output}, {feedback}, and {num_scenes} placeholders.

For example:
Story: {story}
Previous: {previous_output}
Feedback: {feedback}
Revise:"""


scene_prompts_config = ScenePromptsConfig()
