"""
Sandbox for testing the creepypasta pipeline.
Run from v2/: uv run python src/sandbox.py
"""

import json
import logging

from dotenv import load_dotenv
load_dotenv()

from langgraph.types import Command

from graph.builder import compile_graph
from graph.state import CreepypastaState
from config.base import BaseConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TEST_THREAD = {
    "thread_id": "test_001",
    "title": "I found a door in my basement that wasn't there yesterday",
    "content": """I've lived in this house for 15 years. I know every inch of it.

But last night, I went down to grab a beer from the basement fridge, and there it was. A door.
Wooden, old-looking, with a brass handle that was ice cold to the touch.

I stood there for what felt like hours, just staring at it. The door wasn't there yesterday.
I would have noticed. I go down there every single day.

The worst part? I can hear something breathing on the other side.

It's been 6 hours now. The breathing hasn't stopped. And I swear... I swear the door is closer
to the stairs than it was before.

I don't know what to do. Should I open it? Should I call someone? Who do you even call for
something like this?

Update: It's been 12 hours. The door is definitely closer. And now I can hear whispers.

Update 2: I think whatever is behind that door... knows I'm listening.""",
    "author": "u/BasementDweller99",
    "url": "https://reddit.com/r/nosleep/comments/test001",
}


def display_interrupt(interrupt_value: dict) -> None:
    """Display interrupt data for user review."""
    print("\n" + "=" * 60)
    print(f"REVIEW REQUESTED: {interrupt_value.get('type', 'unknown')}")
    print("=" * 60)

    output = interrupt_value.get("output")
    if isinstance(output, str):
        print(f"\n{output}\n")
    elif isinstance(output, list):
        for i, item in enumerate(output, 1):
            print(f"\n{i}. {item}")
        print()
    elif isinstance(output, dict):
        print(json.dumps(output, indent=2))
    else:
        print(output)

    print("=" * 60)
    print("Type 'approve' to continue, or provide feedback to regenerate:")
    print("=" * 60)


def run_pipeline(enable_reviews: bool = False):
    """Run the full pipeline with interactive review loop."""
    logger.info("Compiling graph...")
    app = compile_graph()

    # Use the thread_id from TEST_THREAD for run directory
    thread_id = TEST_THREAD["thread_id"]

    # Create run directory
    config = BaseConfig()
    run_dir = config.RUNS_PATH / thread_id
    run_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Run directory: {run_dir}")

    initial_state: CreepypastaState = {
        "enable_reviews": enable_reviews,
        "reddit_thread": TEST_THREAD,
        "run_dir": str(run_dir),
        "triage": None,
        "script": None,
        "scene_prompts": None,
        "thumbnail_prompt": None,
        "yt_title": None,
        "yt_description": None,
        "audio": None,
        "scene_images": None,
        "thumbnail": None,
        "current_feedback": None,
        "status": "started",
        "message": None,
    }

    config = {"configurable": {"thread_id": thread_id}}

    logger.info(f"Starting pipeline with thread_id: {thread_id}")
    logger.info(f"Reviews enabled: {enable_reviews}")

    # Initial invocation
    app.invoke(initial_state, config=config)

    # Review loop - keep checking for interrupts and handling them
    while True:
        state = app.get_state(config)

        # Check if there's an interrupt pending
        if state.tasks and any(task.interrupts for task in state.tasks):
            # Get the interrupt value
            for task in state.tasks:
                if task.interrupts:
                    interrupt_value = task.interrupts[0].value
                    display_interrupt(interrupt_value)

                    # Get user input
                    user_input = input("\n> ").strip()

                    # Resume with user's response
                    app.invoke(Command(resume=user_input), config=config)
                    break
        else:
            # No more interrupts, we're done
            break

    # Get final state
    final_state = app.get_state(config).values

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)
    print(f"Status: {final_state.get('status')}")
    print(f"\nYT Title: {final_state.get('yt_title')}")
    print(f"\nYT Description:\n{final_state.get('yt_description')}")
    print("\nScene Prompts:")
    for i, prompt in enumerate(final_state.get('scene_prompts') or [], 1):
        print(f"  {i}. {prompt}")
    print(f"\nThumbnail Prompt: {final_state.get('thumbnail_prompt')}")
    print(f"\nAudio: {final_state.get('audio')}")

    return final_state


def test_tts():
    """Test NeuTTS voice cloning."""
    from pathlib import Path
    from tts import create_tts

    # Reference audio and transcript
    REF_AUDIO = Path("assets/narrators/ghoul.mp3")
    REF_TEXT = "You. You tell the others. Tell them that this is the voice of a serial killer. One so evil that the devil himself... is afraid."  # TODO: add real transcript

    if not REF_AUDIO.exists():
        print(f"Reference audio not found: {REF_AUDIO}")
        return

    logger.info("Loading NeuTTS model (this may take a minute)...")
    tts = create_tts("neutts", "neuphonic/neutts-air", backbone_device="cpu")

    logger.info("Registering voice...")
    tts.register_voice("narrator", REF_AUDIO, REF_TEXT)

    logger.info("Synthesizing test audio...")
    test_text = "A mysterious door appears in my basement overnight. I hear something breathing on the other side. Original story from Reddit: u/BasementDweller99. I've lived in this house for 15 years, but nothing could have prepared me for this."

    audio_bytes = tts.synthesize(
        text=test_text,
        voice_id="narrator",
        output_path=Path("output/test_tts.wav"),
    )

    logger.info(f"Done! Saved to output/test_tts.wav ({len(audio_bytes)} bytes)")


def test_tti():
    """Test Juggernaut XI image generation (CUDA only)."""
    from pathlib import Path
    from tti import create_tti, unload_all_tti

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    logger.info("Loading Juggernaut XI...")
    tti = create_tti("juggernaut")

    prompt = "dark basement with old wooden door, red moonlight through window, horror atmosphere, cinematic lighting, photorealistic, 8k"
    negative_prompt = "bright, cheerful, cartoon, anime, text, watermark"

    logger.info("Generating test image...")
    image = tti.generate(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=1280,
        height=720,
        num_inference_steps=30,
        guidance_scale=7.0,
        seed=42,
        output_path=output_dir / "test_tti.png",
    )

    logger.info(f"Done! Saved to output/test_tti.png ({image.size[0]}x{image.size[1]})")
    unload_all_tti()


def main():
    """Run the full pipeline test."""
    # run_pipeline(enable_reviews=False)
    # test_tts()
    # test_tti()
    pass


if __name__ == "__main__":
    main()
