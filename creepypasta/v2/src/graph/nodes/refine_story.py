"""
Refine story node - cleans and optimizes content for narration.
"""

import logging
from typing import TypedDict

from langgraph.types import Command

from graph.state import CreepypastaState
from config.refine_story import refine_story_config
from llm import create_llm
from infrastructure.json import save_metadata

logger = logging.getLogger(__name__)


class RefineResult(TypedDict):
    """Structured output for story refinement."""
    story: str


def refine_story(state: CreepypastaState) -> Command:
    """
    Clean and enhance the story for narration.

    Removes irrelevant parts, improves flow, enhances atmosphere.
    Supports regeneration with feedback.
    """
    thread = state["reddit_thread"]
    feedback = state["current_feedback"]
    previous_output = state["script"]

    logger.info(f"Refining story: {thread['title'][:50]}...")

    llm = create_llm(
        refine_story_config.LLM_PROVIDER,
        refine_story_config.LLM_MODEL,
        temperature=refine_story_config.LLM_TEMPERATURE,
    )

    if feedback and previous_output:
        logger.info("Regenerating with feedback...")
        user_prompt = refine_story_config.USER_REVIEW_PROMPT.format(
            content=thread["content"],
            previous_output=previous_output,
            feedback=feedback,
        )
    else:
        user_prompt = refine_story_config.USER_PROMPT.format(
            content=thread["content"],
        )

    result: RefineResult = llm.generate_structured(
        prompt=user_prompt,
        schema=RefineResult,
        system_prompt=refine_story_config.SYSTEM_PROMPT,
    )

    script = result["story"]

    logger.info(f"Refined story: {len(script)} chars")

    next_node = "review_story" if state["enable_reviews"] else "write_scene_prompts"

    update = {
        "script": script,
        "current_feedback": None,
        "status": "refined",
    }
    save_metadata(state["run_dir"], {**state, **update})

    return Command(update=update, goto=next_node)
