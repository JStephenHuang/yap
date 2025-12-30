"""
Write thumbnail prompt node - generates YouTube thumbnail image prompt.
"""

import logging
from typing import TypedDict

from langgraph.types import Command

from graph.state import CreepypastaState
from config.thumbnail_prompt import thumbnail_prompt_config
from llm import create_llm
from infrastructure.json import save_metadata

logger = logging.getLogger(__name__)


class ThumbnailPromptResult(TypedDict):
    """Structured output for thumbnail prompt."""
    thumbnail_prompt: str


def write_thumbnail_prompt(state: CreepypastaState) -> Command:
    """
    Generate YouTube thumbnail prompt.

    Creates a single eye-catching thumbnail prompt optimized for:
    - Small size visibility (YouTube browse)
    - Click-through rate (curiosity/dread)
    - No spoilers

    Supports regeneration with feedback.
    """
    script = state["script"]
    reddit_thread = state["reddit_thread"]
    feedback = state["current_feedback"]
    previous_output = state["thumbnail_prompt"]

    title = reddit_thread["title"]

    logger.info("Generating thumbnail prompt...")

    llm = create_llm(
        thumbnail_prompt_config.LLM_PROVIDER,
        thumbnail_prompt_config.LLM_MODEL,
        temperature=thumbnail_prompt_config.LLM_TEMPERATURE,
    )

    system_prompt = thumbnail_prompt_config.SYSTEM_PROMPT.format(
        visual_style=thumbnail_prompt_config.VISUAL_STYLE,
    )

    if feedback and previous_output:
        logger.info("Regenerating with feedback...")
        user_prompt = thumbnail_prompt_config.USER_REVIEW_PROMPT.format(
            title=title,
            story=script,
            previous_output=previous_output,
            feedback=feedback,
        )
    else:
        user_prompt = thumbnail_prompt_config.USER_PROMPT.format(
            title=title,
            story=script,
        )

    result: ThumbnailPromptResult = llm.generate_structured(
        prompt=user_prompt,
        schema=ThumbnailPromptResult,
        system_prompt=system_prompt,
    )

    thumbnail_prompt = result["thumbnail_prompt"]

    logger.info(f"Generated thumbnail prompt: {thumbnail_prompt[:50]}...")

    next_node = "review_thumbnail_prompt" if state["enable_reviews"] else "write_yt_metadata"

    update = {
        "thumbnail_prompt": thumbnail_prompt,
        "current_feedback": None,
        "status": "thumbnail_prompt_written",
    }
    save_metadata(state["run_dir"], {**state, **update})

    return Command(update=update, goto=next_node)
