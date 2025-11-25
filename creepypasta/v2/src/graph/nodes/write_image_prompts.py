"""
Write image prompts node - generates TTI prompts for story visualization.
"""

import logging

from langgraph.types import Command

from graph.state import CreepypastaState
# from services.image_prompts import generate_image_prompts

logger = logging.getLogger(__name__)


def write_image_prompts(state: CreepypastaState) -> Command:
    """
    Generate image prompts for story visualization.

    Creates:
    - Ordered list of scene prompts (follow story progression)
    - Thumbnail prompt (eye-catching, represents story theme)
    """
    refined_script = state.get("refined_script")
    if not refined_script:
        raise RuntimeError("No refined_script in state - should not reach write_image_prompts")

    logger.info("Generating image prompts...")

    # TODO: Call image prompt service
    # result = generate_image_prompts(refined_script)

    # Pseudo:
    # 1. Split script into scenes/segments (by paragraph or narrative beats)
    # 2. For each segment, generate descriptive TTI prompt
    #    - Visual style consistent (e.g., "dark atmospheric, horror, cinematic")
    #    - Descriptive but concise (DALL-E/Midjourney friendly)
    #    - No text in images
    # 3. Generate thumbnail prompt separately
    #    - More dramatic, eye-catching
    #    - Represents core theme/hook

    # Structured output schema:
    # class ImagePromptsResult(TypedDict):
    #     scene_prompts: list[str]  # Ordered by story progression
    #     thumbnail_prompt: str

    scene_prompts = [
        "TODO: scene 1 prompt",
        "TODO: scene 2 prompt",
        "TODO: scene 3 prompt",
    ]
    thumbnail_prompt = "TODO: thumbnail prompt"

    logger.info(f"Generated {len(scene_prompts)} scene prompts + thumbnail")

    return Command(
        update={
            "image_prompts": scene_prompts,
            "thumbnail_prompt": thumbnail_prompt,
            "status": "prompts_written",
        },
        goto="write_metadata"
    )
