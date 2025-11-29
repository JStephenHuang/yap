"""
Sandbox for testing the creepypasta pipeline.
Run from v2/: uv run python src/sandbox.py
"""

import json
import logging
import uuid

from langgraph.types import Command

from graph.builder import compile_graph
from graph.state import CreepypastaState

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

    thread_id = str(uuid.uuid4())

    initial_state: CreepypastaState = {
        "enable_reviews": enable_reviews,
        "reddit_thread": TEST_THREAD,
        "triage": None,
        "refined_script": None,
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

    return final_state


def main():
    """Run the full pipeline test."""
    run_pipeline(enable_reviews=True)


if __name__ == "__main__":
    main()
