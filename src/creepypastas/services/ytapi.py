import os
from pathlib import Path
import logging

import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

from creepypastas.config import Settings
from creepypastas.utils import find_thread, save

logger = logging.getLogger(__name__)


class YouTubeAPI:
    def __init__(
        self,
        csv_path: Path,
        settings: Settings,
        thread_id: str | None = None,
    ):
        self.csv_path = csv_path
        self.settings = settings
        self.df = pd.read_csv(csv_path)
        self.thread_id = thread_id
        self.client_secret_file = self.settings.YOUTUBE_CLIENT_SECRET_FILE

    def _create_service(self, scopes: list[str]):
        API_SERVICE_NAME = "youtube"
        API_VERSION = "v3"
        SCOPES = scopes

        creds = None
        working_dir = Path.cwd()
        token_dir = "token_files"
        token_file = f"token_{API_SERVICE_NAME}_{API_VERSION}.json"

        token_dir_path = working_dir / token_dir
        if not token_dir_path.exists():
            token_dir_path.mkdir()

        token_path = token_dir_path / token_file

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            token_path.write_text(creds.to_json())

        try:
            service = build(
                API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False
            )
            logger.info(
                f"{API_SERVICE_NAME} {API_VERSION} service created successfully"
            )
            return service
        except Exception as e:
            if token_path.exists():
                token_path.unlink()

            raise Exception(
                f"Failed to create service instance for {API_SERVICE_NAME}: {e}"
            )

    def _upload_video(
        self,
        service,
        video_title: str,
        video_description: str,
        video_file: str,
    ) -> str | None:
        request_body = {
            "snippet": {
                "title": video_title,
                "description": video_description,
                "categoryId": "24",  # Entertainment
                "tags": self.settings.YOUTUBE_DEFAULT_TAGS,
            },
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False},
            "notifySubscribers": False,
        }

        try:
            logger.info(f"Uploading video for thread {thread_id}...")

            response = (
                service.videos()
                .insert(
                    part="snippet,status",
                    body=request_body,
                    media_body=MediaFileUpload(video_file),
                )
                .execute()
            )
            return response.get("id")
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
            return None

    def _set_thumbnail(self, service, video_id: str, thumbnail_file: str) -> None:
        if not Path(thumbnail_file).exists():
            logger.warning(f"Thumbnail file {thumbnail_file} does not exist, skipping.")
            return

        try:
            service.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(thumbnail_file)
            ).execute()
            logger.info(f"Thumbnail set for video {video_id}")
        except Exception as e:
            logger.error(f"Failed to set thumbnail for video {video_id}: {e}")

    def _process_thread(
        self, service, row: pd.Series, idx: int, thread_id: str
    ) -> None:
        status = row.get("status")
        youtube_ready = row.get("youtube_ready")
        if status == "rejected" or not youtube_ready:
            logger.info(
                f"Thread {thread_id}'s status: {status}, youtube_ready: {youtube_ready}, skipping."
            )
            return

        output_dir = self.settings.DATA_DIR / thread_id
        video_path = output_dir / "final_video.mp4"
        if not video_path.exists():
            logger.warning(f"Video file not found for thread {thread_id}, skipping.")
            return

        title = row.get("title", f"Creepypasta Story - {thread_id}")
        description = row.get("description", "A chilling creepypasta narration.")

        video_id = self._upload_video(service, title, description, str(video_path))

        # Set thumbnail using first image if available
        thumbnail_path = row.get("thumbnail_path")

        self._set_thumbnail(service, video_id, thumbnail_path)

        # Update CSV
        self.df.at[idx, "youtube_video_id"] = video_id
        self.df.at[idx, "youtube_link"] = f"https://www.youtube.com/watch?v={video_id}"
        self.df.at[idx, "status"] = "uploaded"
        self.df.at[idx, "used_for_video"] = True

        save(self.csv_path, self.df)

        logger.info(
            f"Uploaded video for thread {thread_id}: https://www.youtube.com/watch?v={video_id}"
        )

    def run(self) -> None:
        service = self._create_service(self.settings.YOUTUBE_SCOPES)

        try:
            if not service:
                logger.error("Failed to create YouTube service, aborting.")
                return

            if self.thread_id:
                # Process only the specified thread_id
                row, idx = find_thread(self.thread_id, self.df)

                self._process_thread(service, row, idx, self.thread_id)
                return
                # Process all eligible threads
            for idx, row in self.df.iterrows():
                thread_id = row.get("thread_id")
                self._process_thread(service, row, idx, thread_id)

        except Exception as e:
            logger.error(f"Error occurred while processing threads: {e}")
