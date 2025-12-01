"""
Narrate story node - converts script to speech using TTS.
"""

import logging
from pathlib import Path

from langgraph.types import Command

from graph.state import CreepypastaState
from config.tts import tts_config
from tts import create_tts, unload_all_tts
from llm import unload_all_llms
from infrastructure.json import save_metadata

logger = logging.getLogger(__name__)


def narrate_story(state: CreepypastaState) -> Command:
    """
    Generate narration audio from the script.

    Uses voice cloning TTS to produce audio in the configured speaker's voice.
    Unloads LLMs before loading TTS to free memory.
    """
    script = state["script"]
    thread = state["reddit_thread"]

    if not script:
        logger.error("No script available for audio generation")
        return Command(
            update={
                "status": "error",
                "message": "No script for audio generation",
            },
            goto="__end__",
        )

    logger.info(f"Generating audio for: {thread['title'][:50]}...")
    logger.info(f"Script length: {len(script)} chars")

    # Unload all LLMs to free memory before loading TTS
    logger.info("Unloading LLMs to free memory...")
    unload_all_llms()

    # Get speaker config
    speaker_name = tts_config.DEFAULT_SPEAKER
    speaker = tts_config.SPEAKERS.get(speaker_name)

    if not speaker:
        logger.error(f"Speaker '{speaker_name}' not found in config")
        return Command(
            update={
                "status": "error",
                "message": f"Speaker '{speaker_name}' not configured",
            },
            goto="__end__",
        )

    # Load TTS model
    logger.info(f"Loading TTS model: {tts_config.MODEL}")
    tts = create_tts(
        tts_config.PROVIDER,
        tts_config.MODEL,
        device=tts_config.DEVICE,
    )

    # Register voice
    logger.info(f"Using voice: {speaker.name}")
    tts.register_voice(speaker.name, speaker.audio, speaker.transcript)

    # Output to run directory
    run_dir = Path(state["run_dir"])
    output_path = run_dir / "narration.wav"

    # Synthesize
    logger.info("Synthesizing audio (this may take a while on CPU)...")
    tts.synthesize(
        text=script,
        voice_id=speaker.name,
        output_path=output_path,
    )

    logger.info(f"Audio saved to: {output_path}")

    # Unload TTS to free memory
    logger.info("Unloading TTS...")
    unload_all_tts()

    update = {
        "audio": str(output_path),
        "status": "completed",
    }
    
    save_metadata(state["run_dir"], {**state, **update})
    return Command(update=update, goto="generate_images")
