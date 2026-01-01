class ScenePromptsConfig:
    """Scene prompts generation configuration"""

    LLM_PROVIDER: str = "langchain-groq"
    LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.5

    # Fixed number of scenes
    NUM_SCENES: int = 3

    # Visual style applied to all prompts
    VISUAL_STYLE: str = "dark atmospheric horror, cinematic lighting"

    SYSTEM_PROMPT: str = """You are a visual director for horror narration videos.

Create {num_scenes} image generation prompts for key story moments.

CRITICAL RULES:
- Prompts must follow story CHRONOLOGICALLY (e.g. scene 1: beginning → scene 2: middle → scene 3: climax)
- Each captures a KEY VISUAL MOMENT viewers see while listening
- Keep it short and concise (1 sentence)
- Avoid too much descrption and focus on the specific visual of the scene
- NO text/words/letters in images
- NO clear faces (use shadows, back angles, silhouettes - avoids AI artifacts)
- Each prompt is standalone (image generator has no cross-prompt context)
- Keep the images SAFE for work (no nudity, gore, or overly graphic content, no graphic blood)

STYLE: {visual_style}
"""

    USER_PROMPT: str = """Story:

{story}

Generate {num_scenes} scene prompts:"""

    USER_REVIEW_PROMPT: str = """Story:

{story}

Your previous prompts:
{previous_output}

Feedback to address:
{feedback}

Revise ONLY the prompts mentioned in the feedback. Keep the others unchanged.
Return all {num_scenes} prompts in order."""


scene_prompts_config = ScenePromptsConfig()
