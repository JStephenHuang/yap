"""
Triage node for langgraph pipeline.
Pure orchestrator - delegates all logic to triage service.
"""

import logging

from graph.state import CreepypastaState
from services.triage import (
    evaluate_post,
)

from infrastructure.database import RedditThreadRepositorySingleton

from langgraph.types import Command

logger = logging.getLogger(__name__)


def triage(state: CreepypastaState) -> CreepypastaState:
    """
    Evaluate posts until one is approved.

    Fetches pending posts from database, evaluates each with LLM,
    and returns the first approved post's thread_id in state.
    """
    
    if state.get("reddit_thread"):
        return Command(
            update={
                "status": "triaged",
                "triage_result": {
                    "decision": "approved",
                    "reason": "manual triage",
                },
            },
            goto="plan"
        )
        
    repo = RedditThreadRepositorySingleton()
    post = repo.get_single_raw()
    
    # should never happen check before going through a run if there are raw posts
    if not post:
        raise RuntimeError("No posts - should have been caught in pre-flight")
        
    logger.info(f"Evaluating: {post['title']}")

    result = evaluate_post(post)
    decision = result.get("decision")
    
    repo.update_status(post["thread_id"], decision)

    if decision== "approved":
        return Command(
            update={
                "reddit_thread": post,
                "status": "triaged",
                "triage_result": result,
            },
            goto="plan"
        )
        
    return Command(
        update={
            "reddit_thread": post,
            "status": "triaged",
            "triage_result": result,
        },
        goto="triage"
    )