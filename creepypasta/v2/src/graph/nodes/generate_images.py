"""
Generate images node - creates scene images and thumbnail using TTI.
"""

import logging
from pathlib import Path

from langgraph.types import Command

from graph.state import CreepypastaState
from config.tti import tti_config
from tti import create_tti, unload_all_tti
from tts import unload_all_tts
from infrastructure.json import save_metadata

logger = logging.getLogger(__name__)


def generate_images(state: CreepypastaState) -> Command:
    """
    Generate scene images and thumbnail from prompts.

    Uses Juggernaut XI to generate images. Unloads TTS before loading TTI.
    """
    scene_prompts = state["scene_prompts"]
    thumbnail_prompt = state["thumbnail_prompt"]
    run_dir = Path(state["run_dir"])

    if not scene_prompts:
        logger.error("No scene prompts available")
        return Command(
            update={"status": "error", "message": "No scene prompts"},
            goto="__end__",
        )

    if not thumbnail_prompt:
        logger.error("No thumbnail prompt available")
        return Command(
            update={"status": "error", "message": "No thumbnail prompt"},
            goto="__end__",
        )

    # Unload TTS to free memory before loading TTI
    logger.info("Unloading TTS to free memory...")
    unload_all_tts()

    # Load TTI
    logger.info("Loading Juggernaut XI...")
    tti = create_tti(tti_config.PROVIDER)

    # Generate scene images
    scene_images = []
    for i, prompt in enumerate(scene_prompts):
        output_path = run_dir / f"scene_{i}.png"
        logger.info(f"Generating scene {i + 1}/{len(scene_prompts)}...")

        tti.generate(
            prompt=prompt,
            negative_prompt=tti_config.NEGATIVE_PROMPT,
            width=tti_config.WIDTH,
            height=tti_config.HEIGHT,
            num_inference_steps=tti_config.NUM_INFERENCE_STEPS,
            guidance_scale=tti_config.GUIDANCE_SCALE,
            output_path=output_path,
        )
        scene_images.append(str(output_path))

    # Generate thumbnail
    thumbnail_path = run_dir / "thumbnail.png"
    logger.info("Generating thumbnail...")
    tti.generate(
        prompt=thumbnail_prompt,
        negative_prompt=tti_config.NEGATIVE_PROMPT,
        width=tti_config.WIDTH,
        height=tti_config.HEIGHT,
        num_inference_steps=tti_config.NUM_INFERENCE_STEPS,
        guidance_scale=tti_config.GUIDANCE_SCALE,
        output_path=thumbnail_path,
    )

    # Unload TTI
    logger.info("Unloading TTI...")
    unload_all_tti()

    update = {
        "scene_images": scene_images,
        "thumbnail": str(thumbnail_path),
        "status": "completed",
    }

    save_metadata(state["run_dir"], {**state, **update})
    return Command(update=update, goto="create_video")
