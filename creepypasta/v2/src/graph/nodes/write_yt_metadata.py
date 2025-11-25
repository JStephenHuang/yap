"""
Write metadata node - generates YouTube title and description.
"""

import logging

from langgraph.types import Command

from graph.state import CreepypastaState
# from services.metadata import generate_metadata

logger = logging.getLogger(__name__)


def write_yt_metadata(state: CreepypastaState) -> Command:
    """
    Generate YouTube metadata for the video.

    Creates:
    - Title (clickable, SEO-friendly, matches creepypasta style)
    - Description (includes story hook, tags, links)
    """
    refined_script = state.get("refined_script")
    thread = state.get("reddit_thread")

    if not refined_script or not thread:
        raise RuntimeError("Missing refined_script or reddit_thread in state")

    logger.info("Generating YouTube metadata...")

    # TODO: Call metadata service
    # result = generate_metadata(refined_script, thread["title"])

    # Pseudo:
    # 1. Generate title
    #    - Clickbait but not misleading
    #    - Include hooks: "True Story", "Don't Read Alone", etc.
    #    - SEO keywords for creepypasta/horror
    #    - Max ~60 chars for YouTube display
    #
    # 2. Generate description
    #    - First 2 lines visible in search (make them count)
    #    - Story hook/teaser
    #    - Credit original source (reddit link)
    #    - Hashtags: #creepypasta #horror #scary
    #    - Timestamps placeholder (filled after TTS)

    # Structured output schema:
    # class MetadataResult(TypedDict):
    #     yt_title: str
    #     yt_description: str

    yt_title = "TODO: YouTube title"
    yt_description = "TODO: YouTube description"

    logger.info(f"Generated title: {yt_title}")

    return Command(
        update={
            "yt_title": yt_title,
            "yt_description": yt_description,
            "status": "metadata_written",
        },
        goto="await_approval"
    )
