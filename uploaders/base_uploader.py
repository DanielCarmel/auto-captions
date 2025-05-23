"""
Base uploader class for social media platforms.
"""

from abc import ABC, abstractmethod
import os
from typing import Dict, Optional, List


class BaseUploader(ABC):
    """Base class for all social media uploaders."""

    def __init__(
        self, credentials_file: Optional[str] = None, credentials: Optional[Dict] = None
    ):
        """
        Initialize the uploader with credentials.

        Args:
            credentials_file: Path to JSON file containing credentials
            credentials: Dictionary with credential information
        """
        self.authenticated = False
        self.credentials = {}

        if credentials_file and os.path.exists(credentials_file):
            self._load_credentials_from_file(credentials_file)
        elif credentials:
            self.credentials = credentials

    def _load_credentials_from_file(self, credentials_file: str) -> None:
        """Load credentials from a JSON file."""
        import json

        try:
            with open(credentials_file, "r") as f:
                self.credentials = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading credentials: {e}")

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform API."""
        pass

    @abstractmethod
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        **kwargs,
    ) -> str:
        """
        Upload a video to the platform.

        Args:
            video_path: Path to the video file
            title: Video title
            description: Video description
            tags: List of tags/hashtags
            **kwargs: Platform-specific arguments
        Returns:
            URL or ID of the uploaded video
        """
        pass
