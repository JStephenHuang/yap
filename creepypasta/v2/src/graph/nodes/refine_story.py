"""
Refine story node - cleans and optimizes content for narration.
"""

import logging
from typing import TypedDict

from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate

from graph.state import CreepypastaState
from config.refine_story import refine_story_config
from infrastructure.llm import create_structured_llm

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
    previous_output = state["refined_script"]

    logger.info(f"Refining story: {thread['title'][:50]}...")

    structured_llm = create_structured_llm(
        refine_story_config.LLM_PROVIDER,
        refine_story_config.LLM_MODEL,
        RefineResult,
        temperature=refine_story_config.LLM_TEMPERATURE,
    )

    if feedback and previous_output:
        logger.info("Regenerating with feedback...")
        prompt = ChatPromptTemplate([
            ("system", refine_story_config.SYSTEM_PROMPT),
            ("human", refine_story_config.USER_REVIEW_PROMPT),
        ])
        chain = prompt | structured_llm
        result: RefineResult = chain.invoke({
            "content": thread["content"],
            "previous_output": previous_output,
            "feedback": feedback,
        })
    else:
        prompt = ChatPromptTemplate([
            ("system", refine_story_config.SYSTEM_PROMPT),
            ("human", refine_story_config.USER_PROMPT),
        ])
        chain = prompt | structured_llm
        result: RefineResult = chain.invoke({"content": thread["content"]})

    refined_script = result["story"]

    logger.info(f"Refined story: {len(refined_script)} chars")

    next_node = "review_story" if state["enable_reviews"] else "write_scene_prompts"

    return Command(
        update={
            "refined_script": refined_script,
            "current_feedback": None,
            "status": "refined",
        },
        goto=next_node,
    )
