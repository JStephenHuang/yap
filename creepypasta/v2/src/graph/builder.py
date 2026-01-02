"""
Graph builder - assembles the creepypasta generation pipeline.
"""

from langgraph.graph import StateGraph

from graph.state import CreepypastaState
from graph.nodes.triage import triage
from graph.nodes.refine_story import refine_story
from graph.nodes.write_scene_prompts import write_scene_prompts
from graph.nodes.write_thumbnail_prompt import write_thumbnail_prompt
from graph.nodes.write_yt_metadata import write_yt_metadata
from graph.nodes.narrate_story import narrate_story
from graph.nodes.generate_images import generate_images
from graph.nodes.create_video import create_video
from graph.nodes.review import (
    review_story,
    review_scene_prompts,
    review_thumbnail_prompt,
    review_yt_metadata,
    review_video,
)
from graph.nodes.upload_to_youtube import upload_to_youtube
from infrastructure.database import create_checkpointer


def build_graph() -> StateGraph:
    """
    Build the creepypasta generation graph.

    Flow (with reviews enabled):
        triage → refine_story → review_story → write_scene_prompts →
        review_scene_prompts → write_thumbnail_prompt → review_thumbnail_prompt →
        write_yt_metadata → review_yt_metadata → narrate_story → END

    Flow (with reviews disabled):
        triage → refine_story → write_scene_prompts →
        write_thumbnail_prompt → write_yt_metadata → narrate_story → END

    Returns:
        Uncompiled StateGraph (call .compile() with checkpointer to use).
    """
    graph = StateGraph(CreepypastaState)

    # Generation nodes
    graph.add_node("triage", triage)
    graph.add_node("refine_story", refine_story)
    graph.add_node("write_scene_prompts", write_scene_prompts)
    graph.add_node("write_thumbnail_prompt", write_thumbnail_prompt)
    graph.add_node("write_yt_metadata", write_yt_metadata)
    graph.add_node("narrate_story", narrate_story)
    graph.add_node("generate_images", generate_images)  # Not wired yet
    graph.add_node("create_video", create_video)  # Not wired yet

    # Review nodes
    graph.add_node("review_story", review_story)
    graph.add_node("review_scene_prompts", review_scene_prompts)
    graph.add_node("review_thumbnail_prompt", review_thumbnail_prompt)
    graph.add_node("review_yt_metadata", review_yt_metadata)
    graph.add_node("review_video", review_video)  # Not wired yet

    # Upload nodes
    graph.add_node("upload_to_youtube", upload_to_youtube)  # Not wired yet

    # Entry point
    graph.set_entry_point("triage")

    return graph


def compile_graph():
    """
    Build and compile the graph with checkpointer.

    Returns:
        Compiled graph ready for invocation.
    """
    graph = build_graph()
    checkpointer = create_checkpointer()

    return graph.compile(checkpointer=checkpointer)
