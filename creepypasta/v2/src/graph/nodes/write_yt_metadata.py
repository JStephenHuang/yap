"""
Write YouTube metadata node - generates title and description.
"""

import logging
from typing import TypedDict

from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate

from graph.state import CreepypastaState
from config.yt_metadata import yt_metadata_config
from infrastructure.llm import create_structured_llm

logger = logging.getLogger(__name__)


class YTMetadataResult(TypedDict):
    """Structured output for YouTube metadata."""
    yt_title: str
    yt_description: str


def write_yt_metadata(state: CreepypastaState) -> Command:
    """
    Generate YouTube metadata for the video.

    Creates:
    - Title (clickable, SEO-friendly, max 60 chars)
    - Description (hook, context, credits, hashtags)

    Supports regeneration with feedback.
    """
    refined_script = state["refined_script"]
    thread = state["reddit_thread"]
    feedback = state["current_feedback"]
    previous_title = state["yt_title"]
    previous_description = state["yt_description"]

    original_title = thread["title"]
    story_preview = refined_script[:800]

    logger.info("Generating YouTube metadata...")

    structured_llm = create_structured_llm(
        yt_metadata_config.LLM_PROVIDER,
        yt_metadata_config.LLM_MODEL,
        YTMetadataResult,
        temperature=yt_metadata_config.LLM_TEMPERATURE,
    )

    if feedback and previous_title:
        logger.info("Regenerating with feedback...")
        prompt = ChatPromptTemplate([
            ("system", yt_metadata_config.SYSTEM_PROMPT),
            ("human", yt_metadata_config.USER_REVIEW_PROMPT),
        ])
        chain = prompt | structured_llm
        result: YTMetadataResult = chain.invoke({
            "original_title": original_title,
            "story_preview": story_preview,
            "author": thread["author"],
            "thread_url": thread["url"],
            "previous_title": previous_title,
            "previous_description": previous_description or "",
            "feedback": feedback,
        })
    else:
        prompt = ChatPromptTemplate([
            ("system", yt_metadata_config.SYSTEM_PROMPT),
            ("human", yt_metadata_config.USER_PROMPT),
        ])
        chain = prompt | structured_llm
        result: YTMetadataResult = chain.invoke({
            "original_title": original_title,
            "story_preview": story_preview,
            "author": thread["author"],
            "thread_url": thread["url"],
        })

    yt_title = result["yt_title"]
    yt_description = result["yt_description"]

    logger.info(f"Generated title: {yt_title}")

    next_node = "review_yt_metadata" if state["enable_reviews"] else "END"

    return Command(
        update={
            "yt_title": yt_title,
            "yt_description": yt_description,
            "current_feedback": None,
            "status": "metadata_written",
        },
        goto=next_node,
    )
