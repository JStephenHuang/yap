"""
Upload to YouTube node - uploads video and sets thumbnail.
"""

import logging
from pathlib import Path

from langgraph.types import Command

from graph.state import CreepypastaState
from config.youtube import youtube_config
from infrastructure.youtube import create_youtube_service, upload_video, set_thumbnail
from infrastructure.json import save_metadata

logger = logging.getLogger(__name__)


def upload_to_youtube(state: CreepypastaState) -> Command:
    """
    Upload video to YouTube and set thumbnail.

    Requires: video, thumbnail, yt_title, yt_description
    Outputs: youtube_link
    """
    video = state["video"]
    thumbnail = state["thumbnail"]
    yt_title = state["yt_title"]
    yt_description = state["yt_description"]
    run_dir = state["run_dir"]

    if not video:
        logger.error("No video available")
        return Command(
            update={"status": "error", "message": "No video to upload"},
            goto="__end__",
        )

    if not yt_title or not yt_description:
        logger.error("Missing YouTube title or description")
        return Command(
            update={"status": "error", "message": "Missing YT metadata"},
            goto="__end__",
        )

    # Create YouTube service
    logger.info("Authenticating with YouTube...")
    service = create_youtube_service(
        client_secret_file=youtube_config.YOUTUBE_CLIENT_SECRET_FILE,
        token_dir=youtube_config.TOKEN_DIR,
        scopes=youtube_config.SCOPES,
    )

    # Upload video
    logger.info(f"Uploading video: {yt_title}")
    video_id = upload_video(
        service=service,
        video_path=Path(video),
        title=yt_title,
        description=yt_description,
        tags=youtube_config.DEFAULT_TAGS,
        category_id=youtube_config.CATEGORY_ID,
        privacy_status=youtube_config.PRIVACY_STATUS,
        made_for_kids=youtube_config.MADE_FOR_KIDS,
        notify_subscribers=youtube_config.NOTIFY_SUBSCRIBERS,
    )

    youtube_link = f"https://www.youtube.com/watch?v={video_id}"
    logger.info(f"Video uploaded: {youtube_link}")

    # Set thumbnail
    if thumbnail:
        logger.info("Setting thumbnail...")
        set_thumbnail(service, video_id, Path(thumbnail))

    update = {
        "youtube_link": youtube_link,
        "status": "uploaded",
    }

    save_metadata(run_dir, {**state, **update})
    logger.info(f"Upload complete: {youtube_link}")

    return Command(update=update, goto="__end__")
