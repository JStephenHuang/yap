"""
Refine story node - cleans and optimizes content for narration.
"""

import logging

from langgraph.types import Command

from graph.state import CreepypastaState
from services.refine import refine_story
from infrastructure.database import RedditThreadRepositorySingleton

logger = logging.getLogger(__name__)


def refine_story_node(state: CreepypastaState) -> Command:
    """
    Clean and enhance the story for narration.

    Takes raw reddit content and:
    - Removes irrelevant parts (edits, thank yous, meta commentary)
    - Paraphrases for better flow
    - Optimizes tone, pacing, suspense for audio narration
    """
    thread = state["reddit_thread"]
    if not thread:
        raise RuntimeError("No reddit_thread in state - should not reach refine_story")

    logger.info(f"Refining story: {thread['title'][:50]}...")

    # TODO: Call refine service
    # refined = refine_story(thread["content"])

    # Pseudo:
    # 1. Send content to LLM with refinement prompt
    # 2. Get back cleaned, narration-ready script
    # 3. Optionally get word count, estimated read time

    refined_script = "TODO: refined content here"

    logger.info(f"Refined story: {len(refined_script)} chars")

    return Command(
        update={
            "refined_script": refined_script,
            "status": "refined",
        },
        goto="write_image_prompts"
    )
