"""
Generic review node factory for human-in-the-loop feedback.
"""

import logging
from typing import Callable, Union

from langgraph.types import Command, interrupt

from graph.state import CreepypastaState

logger = logging.getLogger(__name__)


def create_review_node(
    output_fields: Union[str, list[str]],
    regenerate_node: str,
    next_node: str,
    review_name: str,
) -> Callable[[CreepypastaState], Command]:
    """
    Factory that creates review nodes for human feedback.

    Args:
        output_fields: State field(s) containing output to review (single string or list)
        regenerate_node: Node to route back to if feedback given
        next_node: Node to proceed to if approved
        review_name: Human-readable name for logging

    Returns:
        A node function that interrupts for review and routes accordingly
    """
    fields = [output_fields] if isinstance(output_fields, str) else output_fields

    def review_node(state: CreepypastaState) -> Command:
        if len(fields) == 1:
            output = state[fields[0]]
        else:
            output = {field: state[field] for field in fields}

        logger.info(f"Interrupting for review: {review_name}")

        response = interrupt({
            "type": review_name,
            "output": output,
            "message": f"Review {review_name}. Reply 'approve' or provide feedback.",
        })

        response_stripped = response.strip().lower()

        if response_stripped == "approve":
            logger.info(f"{review_name} approved, proceeding to {next_node}")
            return Command(
                update={"current_feedback": None},
                goto=next_node,
            )
        else:
            logger.info(f"{review_name} feedback received, routing to {regenerate_node}")
            return Command(
                update={"current_feedback": response},
                goto=regenerate_node,
            )

    review_node.__name__ = f"review_{review_name}"
    return review_node


# Pre-built review nodes
review_story = create_review_node(
    output_fields="refined_script",
    regenerate_node="refine_story",
    next_node="write_scene_prompts",
    review_name="refined_script",
)

review_scene_prompts = create_review_node(
    output_fields="scene_prompts",
    regenerate_node="write_scene_prompts",
    next_node="write_thumbnail_prompt",
    review_name="scene_prompts",
)

review_thumbnail_prompt = create_review_node(
    output_fields="thumbnail_prompt",
    regenerate_node="write_thumbnail_prompt",
    next_node="write_yt_metadata",
    review_name="thumbnail_prompt",
)

review_yt_metadata = create_review_node(
    output_fields=["yt_title", "yt_description"],
    regenerate_node="write_yt_metadata",
    next_node="END",
    review_name="yt_metadata",
)
