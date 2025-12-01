"""
YouTube API utilities for video upload.
"""

import logging
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)


def create_youtube_service(
    client_secret_file: str,
    token_dir: str,
    scopes: list[str],
):
    """
    Create authenticated YouTube API service.

    Handles OAuth flow and token refresh.
    """
    creds = None
    token_dir_path = Path(token_dir)
    token_dir_path.mkdir(exist_ok=True)
    token_file = token_dir_path / "token_youtube_v3.json"

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            creds = flow.run_local_server(port=0)

        token_file.write_text(creds.to_json())

    service = build("youtube", "v3", credentials=creds, static_discovery=False)
    logger.info("YouTube service created")
    return service


def upload_video(
    service,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    category_id: str,
    privacy_status: str,
    made_for_kids: bool,
    notify_subscribers: bool,
) -> str:
    """
    Upload video to YouTube.

    Returns:
        Video ID of uploaded video
    """
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id,
            "tags": tags,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
        },
        "notifySubscribers": notify_subscribers,
    }

    logger.info(f"Uploading video: {title}")

    response = (
        service.videos()
        .insert(
            part="snippet,status",
            body=request_body,
            media_body=MediaFileUpload(str(video_path)),
        )
        .execute()
    )

    video_id = response.get("id")
    logger.info(f"Video uploaded: https://www.youtube.com/watch?v={video_id}")
    return video_id


def set_thumbnail(service, video_id: str, thumbnail_path: Path) -> None:
    """Set custom thumbnail for uploaded video."""
    if not thumbnail_path.exists():
        logger.warning(f"Thumbnail not found: {thumbnail_path}")
        return

    service.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(str(thumbnail_path)),
    ).execute()

    logger.info(f"Thumbnail set for video {video_id}")
