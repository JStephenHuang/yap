"""
Write scene prompts node - generates TTI prompts for story visualization.
"""

import json
import logging
from typing import TypedDict

from langgraph.types import Command

from graph.state import CreepypastaState
from config.scene_prompts import scene_prompts_config
from llm import create_llm
from infrastructure.json import save_metadata

logger = logging.getLogger(__name__)


class ScenePromptsResult(TypedDict):
    """Structured output for scene prompts."""
    scene_prompts: list[str]


def write_scene_prompts(state: CreepypastaState) -> Command:
    """
    Generate scene prompts for story visualization.

    Creates ordered list of scene prompts that follow story progression.
    Supports regeneration with feedback.
    """
    script = state["script"]
    feedback = state["current_feedback"]
    previous_output = state["scene_prompts"]

    logger.info("Generating scene prompts...")

    llm = create_llm(
        scene_prompts_config.LLM_PROVIDER,
        scene_prompts_config.LLM_MODEL,
        temperature=scene_prompts_config.LLM_TEMPERATURE,
    )

    system_prompt = scene_prompts_config.SYSTEM_PROMPT.format(
        num_scenes=scene_prompts_config.NUM_SCENES,
        visual_style=scene_prompts_config.VISUAL_STYLE,
    )

    if feedback and previous_output:
        logger.info("Regenerating with feedback...")
        user_prompt = scene_prompts_config.USER_REVIEW_PROMPT.format(
            story=script,
            num_scenes=scene_prompts_config.NUM_SCENES,
            previous_output=json.dumps(previous_output, indent=2),
            feedback=feedback,
        )
    else:
        user_prompt = scene_prompts_config.USER_PROMPT.format(
            story=script,
            num_scenes=scene_prompts_config.NUM_SCENES,
        )

    result: ScenePromptsResult = llm.generate_structured(
        prompt=user_prompt,
        schema=ScenePromptsResult,
        system_prompt=system_prompt,
    )

    scene_prompts = result["scene_prompts"]

    logger.info(f"Generated {len(scene_prompts)} scene prompts")

    next_node = "review_scene_prompts" if state["enable_reviews"] else "write_thumbnail_prompt"

    update = {
        "scene_prompts": scene_prompts,
        "current_feedback": None,
        "status": "scene_prompts_written",
    }
    save_metadata(state["run_dir"], {**state, **update})

    return Command(update=update, goto=next_node)
