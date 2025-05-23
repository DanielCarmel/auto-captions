"""
Integration module for video processing and social media uploading.

This module connects the video processing functionality with social media uploaders
to create an end-to-end solution for processing videos and uploading them to
various social media platforms.
"""

import os
import logging
from typing import Dict, List, Optional, Union

from media_processors.video_processor import VideoProcessor
from uploaders.facebook import FacebookUploader
from uploaders.instagram import InstagramUploader
from uploaders.tiktok import TikTokUploader
from uploaders.youtube import YouTubeUploader


logger = logging.getLogger(__name__)


class SocialMediaDistributor:
    """
    Class for processing videos and distributing them to social media platforms.
    """

    SUPPORTED_PLATFORMS = ["youtube", "facebook", "instagram", "tiktok"]

    def __init__(self, credentials_dir: Optional[str] = None):
        """
        Initialize the SocialMediaDistributor.

        Args:
            credentials_dir: Directory containing platform-specific credential files
                            (e.g., youtube_credentials.json)
        """
        self.video_processor = VideoProcessor()
        self.credentials_dir = credentials_dir
        self.uploaders = {}

        # Load credentials and initialize uploaders if directory provided
        if credentials_dir and os.path.isdir(credentials_dir):
            self._initialize_uploaders()

    def _initialize_uploaders(self):
        """Initialize uploaders with credentials from files."""
        for platform in self.SUPPORTED_PLATFORMS:
            cred_file = os.path.join(
                self.credentials_dir, f"{platform}_credentials.json"
            )
            if os.path.exists(cred_file):
                try:
                    if platform == "youtube":
                        self.uploaders[platform] = YouTubeUploader(
                            credentials_file=cred_file
                        )
                    elif platform == "facebook":
                        self.uploaders[platform] = FacebookUploader(
                            credentials_file=cred_file
                        )
                    elif platform == "instagram":
                        self.uploaders[platform] = InstagramUploader(
                            credentials_file=cred_file
                        )
                    elif platform == "tiktok":
                        self.uploaders[platform] = TikTokUploader(
                            credentials_file=cred_file
                        )
                    logger.info(f"Initialized {platform} uploader")
                except Exception as e:
                    logger.error(f"Failed to initialize {platform} uploader: {e}")

    def set_credentials(self, platform: str, credentials: Dict):
        """
        Set credentials for a specific platform.

        Args:
            platform: One of the supported platforms ("youtube", "facebook", etc.)
            credentials: Dictionary with credential information
        """
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")

        if platform == "youtube":
            self.uploaders[platform] = YouTubeUploader(credentials=credentials)
        elif platform == "facebook":
            self.uploaders[platform] = FacebookUploader(credentials=credentials)
        elif platform == "instagram":
            self.uploaders[platform] = InstagramUploader(credentials=credentials)
        elif platform == "tiktok":
            self.uploaders[platform] = TikTokUploader(credentials=credentials)

        logger.info(f"Set credentials for {platform}")

    def process_and_distribute(
        self,
        input_video_path: str,
        subtitles_path: str,
        output_path: str,
        platforms: List[str],
        metadata: Dict[str, Union[str, List[str]]],
        platform_options: Optional[Dict[str, Dict]] = None,
    ) -> Dict[str, str]:
        """
        Process a video with subtitles and distribute to multiple platforms.

        Args:
            input_video_path: Path to the input video
            subtitles_path: Path to the subtitles file
            output_path: Path for saving the processed video
            platforms: List of platforms to upload to
            metadata: Video metadata (title, description, tags)
            platform_options: Platform-specific options for each uploader

        Returns:
            Dictionary mapping platforms to upload results (URLs or IDs)
        """
        # Process the video with subtitles
        logger.info(f"Processing video: {input_video_path}")

        # For demonstration, we're skipping the actual video processing here
        # In a real implementation, you would call the appropriate video processor methods
        # self.video_processor.add_subtitles_to_video(input_video_path, subtitles_path, output_path)

        # For this example, assume output_path exists after processing
        processed_video_path = output_path

        # Upload to each platform
        results = {}
        for platform in platforms:
            if platform not in self.uploaders:
                logger.warning(f"No uploader configured for {platform}, skipping")
                results[platform] = f"Error: No uploader configured for {platform}"
                continue

            uploader = self.uploaders[platform]

            # Get platform-specific options, if any
            options = platform_options.get(platform, {}) if platform_options else {}

            try:
                logger.info(f"Uploading to {platform}")
                result = uploader.upload_video(
                    video_path=processed_video_path,
                    title=metadata.get("title", ""),
                    description=metadata.get("description", ""),
                    tags=metadata.get("tags", []),
                    **options,
                )
                results[platform] = result
                logger.info(f"Successfully uploaded to {platform}: {result}")
            except Exception as e:
                logger.error(f"Failed to upload to {platform}: {e}")
                results[platform] = f"Error: {str(e)}"

        return results


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Example credentials for demo purposes (would be loaded from files in practice)
    example_credentials = {
        "youtube": {
            "client_id": "YOUR_YOUTUBE_CLIENT_ID",
            "client_secret": "YOUR_YOUTUBE_CLIENT_SECRET",
        },
        "facebook": {
            "access_token": "YOUR_FACEBOOK_ACCESS_TOKEN",
            "page_id": "YOUR_FACEBOOK_PAGE_ID",
        },
    }

    # Initialize distributor
    distributor = SocialMediaDistributor()

    # Set credentials
    distributor.set_credentials("youtube", example_credentials["youtube"])
    distributor.set_credentials("facebook", example_credentials["facebook"])

    # Example metadata
    metadata = {
        "title": "My Awesome Video",
        "description": "This is an amazing video with auto-generated captions",
        "tags": ["audo", "captions", "demo"],
    }

    # Process and distribute
    results = distributor.process_and_distribute(
        input_video_path="assets/videos/video_with_speech.mp4",
        subtitles_path="assets/output/subtitles.srt",
        output_path="assets/output/output_with_captions.mp4",
        platforms=["youtube", "facebook"],
        metadata=metadata,
        platform_options={
            "youtube": {"privacy_status": "unlisted"},
            "facebook": {"scheduled_publish_time": 1716435000},  # Example timestamp
        },
    )
    # Print results
    print("Distribution results:")
    for platform, result in results.items():
        print(f"{platform}: {result}")
