"""
Write thumbnail prompt node - generates YouTube thumbnail image prompt.
"""

import logging
from typing import TypedDict

from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate

from graph.state import CreepypastaState
from config.thumbnail_prompt import thumbnail_prompt_config
from infrastructure.llm import create_structured_llm

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
    refined_script = state["refined_script"]
    reddit_thread = state["reddit_thread"]
    feedback = state["current_feedback"]
    previous_output = state["thumbnail_prompt"]

    title = reddit_thread["title"]
    story_preview = refined_script[:500]

    logger.info("Generating thumbnail prompt...")

    structured_llm = create_structured_llm(
        thumbnail_prompt_config.LLM_PROVIDER,
        thumbnail_prompt_config.LLM_MODEL,
        ThumbnailPromptResult,
        temperature=thumbnail_prompt_config.LLM_TEMPERATURE,
    )

    if feedback and previous_output:
        logger.info("Regenerating with feedback...")
        prompt = ChatPromptTemplate([
            ("system", thumbnail_prompt_config.SYSTEM_PROMPT),
            ("human", thumbnail_prompt_config.USER_REVIEW_PROMPT),
        ])
        chain = prompt | structured_llm
        result: ThumbnailPromptResult = chain.invoke({
            "title": title,
            "story_preview": story_preview,
            "visual_style": thumbnail_prompt_config.VISUAL_STYLE,
            "previous_output": previous_output,
            "feedback": feedback,
        })
    else:
        prompt = ChatPromptTemplate([
            ("system", thumbnail_prompt_config.SYSTEM_PROMPT),
            ("human", thumbnail_prompt_config.USER_PROMPT),
        ])
        chain = prompt | structured_llm
        result: ThumbnailPromptResult = chain.invoke({
            "title": title,
            "story_preview": story_preview,
            "visual_style": thumbnail_prompt_config.VISUAL_STYLE,
        })

    thumbnail_prompt = result["thumbnail_prompt"]

    logger.info(f"Generated thumbnail prompt: {thumbnail_prompt[:50]}...")

    next_node = "review_thumbnail_prompt" if state["enable_reviews"] else "write_yt_metadata"

    return Command(
        update={
            "thumbnail_prompt": thumbnail_prompt,
            "current_feedback": None,
            "status": "thumbnail_prompt_written",
        },
        goto=next_node,
    )
