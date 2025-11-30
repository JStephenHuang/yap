"""
Write scene prompts node - generates TTI prompts for story visualization.
"""

import json
import logging
from typing import TypedDict

from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate

from graph.state import CreepypastaState
from config.scene_prompts import scene_prompts_config
from infrastructure.llm import create_structured_llm

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
    refined_script = state["refined_script"]
    feedback = state["current_feedback"]
    previous_output = state["scene_prompts"]

    logger.info("Generating scene prompts...")

    structured_llm = create_structured_llm(
        scene_prompts_config.LLM_PROVIDER,
        scene_prompts_config.LLM_MODEL,
        ScenePromptsResult,
        temperature=scene_prompts_config.LLM_TEMPERATURE,
    )

    if feedback and previous_output:
        logger.info("Regenerating with feedback...")
        prompt = ChatPromptTemplate([
            ("system", scene_prompts_config.SYSTEM_PROMPT),
            ("human", scene_prompts_config.USER_REVIEW_PROMPT),
        ])
        chain = prompt | structured_llm
        result: ScenePromptsResult = chain.invoke({
            "story": refined_script,
            "num_scenes": scene_prompts_config.NUM_SCENES,
            "visual_style": scene_prompts_config.VISUAL_STYLE,
            "previous_output": json.dumps(previous_output, indent=2),
            "feedback": feedback,
        })
    else:
        prompt = ChatPromptTemplate([
            ("system", scene_prompts_config.SYSTEM_PROMPT),
            ("human", scene_prompts_config.USER_PROMPT),
        ])
        chain = prompt | structured_llm
        result: ScenePromptsResult = chain.invoke({
            "story": refined_script,
            "num_scenes": scene_prompts_config.NUM_SCENES,
            "visual_style": scene_prompts_config.VISUAL_STYLE,
        })

    scene_prompts = result["scene_prompts"]

    logger.info(f"Generated {len(scene_prompts)} scene prompts")

    next_node = "review_scene_prompts" if state["enable_reviews"] else "write_thumbnail_prompt"

    return Command(
        update={
            "scene_prompts": scene_prompts,
            "current_feedback": None,
            "status": "scene_prompts_written",
        },
        goto=next_node,
    )
