"""
Triage service - business logic for evaluating reddit posts.
"""

import logging
from typing import TypedDict, Literal

from langchain_core.prompts import ChatPromptTemplate

from config.triage import triage_config
from infrastructure.llm import create_structured_llm
from infrastructure.database import RedditThreadRow


class TriageResult(TypedDict):
    """Structured output for triage evaluation."""
    decision: Literal["approve", "reject"]
    reason: str

logger = logging.getLogger(__name__)

def evaluate_post(post: RedditThreadRow) -> TriageResult:
    """
    LLM evaluates if post is good for creepypasta.
    Returns (decision, reason) where decision is 'approve' or 'reject'.
    """
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

    return result