"""
Main entry point for the creepypasta pipeline.

Usage:
    uv run python src/main.py run              # Process next thread from db
    uv run python src/main.py run --no-review  # Auto-approve all stages
    uv run python src/main.py test             # Run with test data (no db)
    uv run python src/main.py resume <id>      # Resume from checkpoint
    uv run python src/main.py status           # Show db queue stats

First, scrape stories:
    uv run scrape-reddit
"""

import argparse
import logging
import sys
import uuid

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.logging import RichHandler
from rich import print_json

from langgraph.types import Command

from graph.builder import compile_graph
from graph.state import CreepypastaState
from config.base import BaseConfig
from infrastructure.database import RedditThreadRepositorySingleton

console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)]
)
logger = logging.getLogger(__name__)


def display_interrupt(interrupt_value: dict) -> None:
    """Display interrupt data for user review."""
    review_type = interrupt_value.get("type", "unknown")

    console.print()
    console.rule(f"[bold yellow]REVIEW: {review_type}[/bold yellow]")

    if "message" in interrupt_value:
        console.print(f"\n{interrupt_value['message']}\n")

    output = interrupt_value.get("output")
    if isinstance(output, str):
        console.print(Panel(output, border_style="dim"))
    elif isinstance(output, list):
        for i, item in enumerate(output, 1):
            console.print(f"  [cyan]{i}.[/cyan] {item}")
    elif isinstance(output, dict):
        print_json(data=output)

    console.print()
    console.rule("[dim]Type 'approve' to continue, or provide feedback[/dim]")


def review_loop(app, config: dict) -> dict:
    """Handle interrupt/review loop until pipeline completes."""
    while True:
        state = app.get_state(config)

        if state.tasks and any(task.interrupts for task in state.tasks):
            for task in state.tasks:
                if task.interrupts:
                    interrupt_value = task.interrupts[0].value
                    display_interrupt(interrupt_value)

                    user_input = Prompt.ask("\n[bold green]>[/bold green]")
                    app.invoke(Command(resume=user_input), config=config)
                    break
        else:
            break

    return app.get_state(config).values


def run_pipeline(
    reddit_thread: dict | None = None,
    enable_reviews: bool = True,
) -> dict:
    """
    Run the full pipeline.

    Args:
        reddit_thread: If None, triage fetches from db. Otherwise uses this.
        enable_reviews: Whether to pause for human review at each stage.

    Returns:
        Final state dict
    """
    app = compile_graph()

    thread_id = reddit_thread["thread_id"] if reddit_thread else str(uuid.uuid4())[:8]

    base_config = BaseConfig()
    run_dir = base_config.RUNS_PATH / thread_id
    run_dir.mkdir(parents=True, exist_ok=True)

    initial_state: CreepypastaState = {
        "enable_reviews": enable_reviews,
        "reddit_thread": reddit_thread,
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
        "video": None,
        "youtube_link": None,
        "current_feedback": None,
        "checkpoint_thread_id": thread_id,  # Save for resume
        "status": "started",
        "message": None,
    }

    config = {"configurable": {"thread_id": thread_id}}

    # Show checkpoint ID prominently so user can resume if needed
    console.print()
    console.print(Panel(
        f"[bold]{thread_id}[/bold]\n[dim]Use this ID to resume: uv run python src/main.py resume {thread_id}[/dim]",
        title="[cyan]Checkpoint ID[/cyan]",
        border_style="cyan"
    ))
    console.print()

    logger.info(f"Run directory: {run_dir}")
    logger.info(f"Reviews enabled: {enable_reviews}")

    app.invoke(initial_state, config=config)

    final_state = review_loop(app, config)

    # Summary
    console.print()
    status = final_state.get("status", "unknown")
    status_color = "green" if status in ["completed", "uploaded"] else "yellow"

    summary = f"[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]"
    if final_state.get("video"):
        summary += f"\n[bold]Video:[/bold] {final_state['video']}"
    if final_state.get("youtube_link"):
        summary += f"\n[bold]YouTube:[/bold] [link={final_state['youtube_link']}]{final_state['youtube_link']}[/link]"

    console.print(Panel(summary, title="[bold green]Pipeline Complete[/bold green]", border_style="green"))

    return final_state


def resume_pipeline(checkpoint_thread_id: str) -> dict:
    """Resume a pipeline from checkpoint."""
    logger.info(f"Resuming: {checkpoint_thread_id}")
    app = compile_graph()

    config = {"configurable": {"thread_id": checkpoint_thread_id}}

    app.invoke(None, config=config)

    final_state = review_loop(app, config)

    console.print()
    status = final_state.get("status", "unknown")
    status_color = "green" if status in ["completed", "uploaded"] else "yellow"

    summary = f"[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]"
    if final_state.get("youtube_link"):
        summary += f"\n[bold]YouTube:[/bold] [link={final_state['youtube_link']}]{final_state['youtube_link']}[/link]"

    console.print(Panel(summary, title="[bold green]Pipeline Complete[/bold green]", border_style="green"))

    return final_state


def show_status():
    """Show queue statistics."""
    repo = RedditThreadRepositorySingleton()

    conn = repo._conn
    cursor = conn.execute("""
        SELECT status, COUNT(*) as count
        FROM reddit_threads
        GROUP BY status
        ORDER BY count DESC
    """)

    table = Table(title="Queue Status", show_header=True, header_style="bold cyan")
    table.add_column("Status", style="dim")
    table.add_column("Count", justify="right")

    total = 0
    for row in cursor:
        table.add_row(row["status"], str(row["count"]))
        total += row["count"]

    table.add_section()
    table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")

    console.print()
    console.print(table)

    next_thread = repo.get_single_raw()
    if next_thread:
        console.print()
        console.print(Panel(
            f"[bold]{next_thread['title'][:60]}{'...' if len(next_thread['title']) > 60 else ''}[/bold]\n"
            f"[dim]Score: {next_thread['score']} | r/{next_thread['subreddit']}[/dim]",
            title="[yellow]Next Up[/yellow]",
            border_style="yellow"
        ))
    else:
        console.print()
        console.print("[yellow]Queue empty.[/yellow] Run: [bold]uv run scrape-reddit[/bold]")


def main():
    parser = argparse.ArgumentParser(
        description="Creepypasta video generation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python src/main.py run              # Process next from db
  uv run python src/main.py run --no-review  # Skip reviews
  uv run python src/main.py test             # Use test data
  uv run python src/main.py resume abc123    # Resume checkpoint
  uv run python src/main.py status           # Show queue stats

First time? Run: uv run scrape-reddit
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    run_parser = subparsers.add_parser("run", help="Process next thread from db")
    run_parser.add_argument("--no-review", action="store_true", help="Auto-approve all")

    test_parser = subparsers.add_parser("test", help="Run with test data (no db)")
    test_parser.add_argument("--no-review", action="store_true", help="Auto-approve all")

    resume_parser = subparsers.add_parser("resume", help="Resume from checkpoint")
    resume_parser.add_argument("thread_id", help="Checkpoint thread_id")

    subparsers.add_parser("status", help="Show queue statistics")

    args = parser.parse_args()

    if args.command == "run":
        repo = RedditThreadRepositorySingleton()
        if not repo.get_single_raw():
            console.print("[yellow]Queue empty.[/yellow] Run: [bold]uv run scrape-reddit[/bold]")
            sys.exit(1)

        run_pipeline(
            reddit_thread=None,
            enable_reviews=not args.no_review,
        )

    elif args.command == "test":
        test_thread = {
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

        run_pipeline(
            reddit_thread=test_thread,
            enable_reviews=not args.no_review,
        )

    elif args.command == "resume":
        resume_pipeline(args.thread_id)

    elif args.command == "status":
        show_status()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
