"""
Triage node - evaluates reddit posts for creepypasta potential.
"""

import logging

from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate

from graph.state import CreepypastaState
from graph.types import TriageResult
from config.triage import triage_config
from infrastructure.llm import create_structured_llm
from infrastructure.database import RedditThreadRepositorySingleton

logger = logging.getLogger(__name__)


def triage(state: CreepypastaState) -> Command:
    """
    Evaluate a single reddit post.

    If approved, proceeds to refine_story.
    If rejected, loops back to triage for next post.
    """
    if state["reddit_thread"]:
        return Command(
            update={
                "status": "triaged",
                "triage_result": {
                    "decision": "approved",
                    "reason": "manual triage",
                },
            },
            goto="refine_story"
        )

    repo = RedditThreadRepositorySingleton()
    post = repo.get_single_raw()

    if not post:
        raise RuntimeError("No posts - should have been caught in pre-flight")

    logger.info(f"Evaluating: {post['title']}")

    # Evaluate with LLM
    prompt = ChatPromptTemplate([
        ("system", triage_config.SYSTEM_PROMPT),
        ("human", triage_config.USER_PROMPT),
    ])

    structured_llm = create_structured_llm(
        triage_config.LLM_PROVIDER,
        triage_config.LLM_MODEL,
        TriageResult,
        temperature=triage_config.LLM_TEMPERATURE,
    )

    chain = prompt | structured_llm

    result: TriageResult = chain.invoke({
        "title": post["title"],
        "text": post["content"][:3000],
        "score": post["score"],
        "upvote_ratio": post["upvote_ratio"],
    })

    decision = result["decision"]
    repo.update_status(post["thread_id"], decision)

    goto = "refine_story" if decision == "approved" else "triage"

    return Command(
        update={
            "reddit_thread": post,
            "status": "triaged",
            "triage_result": result,
        },
        goto=goto
    )
