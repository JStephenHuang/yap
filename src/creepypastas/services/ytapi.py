import os
import datetime
from collections import namedtuple
from pathlib import Path
import logging

import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

from creepypastas.config import Settings
from creepypastas.utils import save


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
        self.client_secret_file = (
            self.settings.YOUTUBE_CLIENT_SECRET_FILE
        )  # Assume this exists in Settings

    def _create_service(self, scopes: list[str]):
        API_SERVICE_NAME = "youtube"
        API_VERSION = "v3"
        SCOPES = scopes

        creds = None
        working_dir = os.getcwd()
        token_dir = "token_files"
        token_file = f"token_{API_SERVICE_NAME}_{API_VERSION}.json"

        if not os.path.exists(os.path.join(working_dir, token_dir)):
            os.mkdir(os.path.join(working_dir, token_dir))

        token_path = os.path.join(working_dir, token_dir, token_file)
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(token_path, "w") as token:
                token.write(creds.to_json())

        try:
            service = build(
                API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False
            )
            logging.info(
                f"{API_SERVICE_NAME} {API_VERSION} service created successfully"
            )
            return service
        except Exception as e:
            logging.error(
                f"Failed to create service instance for {API_SERVICE_NAME}: {e}"
            )
            if os.path.exists(token_path):
                os.remove(token_path)
            return None

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
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
            "notifySubscribers": False,
        }

        media_file = MediaFileUpload(video_file)

        try:
            response = (
                service.videos()
                .insert(part="snippet,status", body=request_body, media_body=media_file)
                .execute()
            )
            return response.get("id")
        except Exception as e:
            logging.error(f"Failed to upload video: {e}")
            return None

    def _set_thumbnail(self, service, video_id: str, thumbnail_file: str) -> None:
        if not Path(thumbnail_file).exists():
            logging.warning(
                f"Thumbnail file {thumbnail_file} does not exist, skipping."
            )
            return

        try:
            service.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(thumbnail_file)
            ).execute()
            logging.info(f"Thumbnail set for video {video_id}")
        except Exception as e:
            logging.error(f"Failed to set thumbnail for video {video_id}: {e}")

    def run(self) -> None:
        scopes = self.settings.YOUTUBE_SCOPES
        service = self._create_service(scopes)
        if not service:
            logging.error("Failed to create YouTube service, aborting.")
            return

        if self.thread_id:
            # Process only the specified thread_id
            row = self.df.loc[self.df["thread_id"] == self.thread_id]
            if row.empty:
                logging.warning(f"No row found for thread {self.thread_id}")
                return
            row = row.iloc[0]
            if row.get("status") != "rejected":
                self._process_thread(service, self.thread_id, row)
            return
        else:
            # Process all eligible threads
            for idx, row in self.df.iterrows():
                thread_id = row.get("thread_id", f"thread_{idx}")
                if self.rerun or row.get("status") != "uploaded":
                    self._process_thread(service, thread_id, row)

    def _process_thread(self, service, thread_id: str, row: pd.Series) -> None:
        output_dir = self.settings.DATA_DIR / thread_id
        video_path = output_dir / "final_video.mp4"
        if not video_path.exists():
            logging.warning(f"Video file not found for thread {thread_id}, skipping.")
            return

        title = row.get("title", f"Creepypasta Story - {thread_id}")
        description = row.get("description", "A chilling creepypasta narration.")

        logging.info(f"Uploading video for thread {thread_id}...")

        video_id = self._upload_video(service, title, description, str(video_path))
        if not video_id:
            return

        # Set thumbnail using first image if available
        thumbnail_path = row.get("thumbnail_path")
        if thumbnail_path:
            self._set_thumbnail(service, video_id, thumbnail_path)

        # Update CSV
        self.df.loc[self.df["thread_id"] == thread_id, "youtube_video_id"] = video_id
        self.df.loc[self.df["thread_id"] == thread_id, "youtube_link"] = (
            f"https://www.youtube.com/watch?v={video_id}"
        )
        self.df.loc[self.df["thread_id"] == thread_id, "status"] = "uploaded"
        save(self.csv_path, self.df)
        logging.info(
            f"Uploaded video for thread {thread_id}: https://www.youtube.com/watch?v={video_id}"
        )
