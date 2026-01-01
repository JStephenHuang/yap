"""
Triage node - evaluates reddit posts for creepypasta potential.
"""

import logging

from langgraph.types import Command

from graph.state import CreepypastaState
from graph.types import TriageResult
from config.triage import triage_config
from llm import create_llm
from infrastructure.database import RedditThreadRepositorySingleton
from infrastructure.json import save_metadata

logger = logging.getLogger(__name__)


def triage(state: CreepypastaState) -> Command:
    """
    Evaluate a single reddit post.

    If approved, proceeds to refine_story.
    If rejected, loops back to triage for next post.
    """
    repo = RedditThreadRepositorySingleton()

    if state["reddit_thread"]:
        update = {
            "status": "triaged",
            "triage": {
                "decision": "approved",
                "reason": "manual triage",
            },
        }
        save_metadata(state["run_dir"], {**state, **update})
        repo.update_status(state["reddit_thread"]["thread_id"], "approved")
        return Command(update=update, goto="refine_story")

    post = repo.get_single_raw()

    if not post:
        raise RuntimeError("No posts - should have been caught in pre-flight")

    logger.info(f"Evaluating: {post['title']}")

    # Evaluate with LLM
    llm = create_llm(
        triage_config.LLM_PROVIDER,
        triage_config.LLM_MODEL,
        temperature=triage_config.LLM_TEMPERATURE,
    )

    user_prompt = triage_config.USER_PROMPT.format(
        title=post["title"],
        text=post["content"],
        score=post["score"],
        upvote_ratio=post["upvote_ratio"],
    )

    result: TriageResult = llm.generate_structured(
        prompt=user_prompt,
        schema=TriageResult,
        system_prompt=triage_config.SYSTEM_PROMPT,
    )

    decision = result["decision"]
    repo.update_status(post["thread_id"], decision)

    goto = "refine_story" if decision == "approved" else "triage"

    update = {
        "reddit_thread": post,
        "status": "triaged",
        "triage_result": result,
    }
    save_metadata(state["run_dir"], {**state, **update})

    return Command(update=update, goto=goto)
