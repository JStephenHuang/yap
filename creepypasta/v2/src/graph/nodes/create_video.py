"""
Create video node - combines images + audio into final video.
"""

import logging
from pathlib import Path

from langgraph.types import Command

from graph.state import CreepypastaState
from config.video import video_config
from infrastructure.ffmpeg import create_video as ffmpeg_create_video
from infrastructure.json import save_metadata
from tti import unload_all_tti

logger = logging.getLogger(__name__)


def create_video(state: CreepypastaState) -> Command:
    """
    Create final video from scene images + narration audio.

    Requires: scene_images, audio, reddit_thread
    Outputs: video path
    """
    scene_images = state["scene_images"]
    audio = state["audio"]
    thread = state["reddit_thread"]
    run_dir = Path(state["run_dir"])

    if not scene_images:
        logger.error("No scene images available")
        return Command(
            update={"status": "error", "message": "No scene images"},
            goto="__end__",
        )

    if not audio:
        logger.error("No audio available")
        return Command(
            update={"status": "error", "message": "No audio"},
            goto="__end__",
        )

    # Unload TTI to free memory
    logger.info("Unloading TTI to free memory...")
    unload_all_tti()

    # Create video
    logger.info("Creating video...")
    output_path = run_dir / "video.mp4"

    # Resolve ambient path relative to project root
    ambient_path = None
    if video_config.AMBIENT_PATH:
        ambient_path = video_config.AMBIENT_PATH
        if not ambient_path.is_absolute():
            ambient_path = Path(__file__).parents[3] / ambient_path

    ffmpeg_create_video(
        image_paths=[Path(p) for p in scene_images],
        audio_path=Path(audio),
        output_path=output_path,
        title=thread["title"],
        intro_duration=video_config.INTRO_DURATION,
        crossfade_duration=video_config.CROSSFADE_DURATION,
        width=video_config.WIDTH,
        height=video_config.HEIGHT,
        framerate=video_config.FRAMERATE,
        font_path=video_config.FONT_PATH,
        title_font_size=video_config.TITLE_FONT_SIZE,
        vcodec=video_config.VCODEC,
        acodec=video_config.ACODEC,
        pix_fmt=video_config.PIX_FMT,
        preset=video_config.PRESET,
        narration_volume=video_config.NARRATION_VOLUME,
        ambient_path=ambient_path,
        ambient_volume=video_config.AMBIENT_VOLUME,
    )

    update = {
        "video": str(output_path),
        "status": "completed",
    }

    save_metadata(state["run_dir"], {**state, **update})
    return Command(update=update, goto="review_video")
