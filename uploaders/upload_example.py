"""
Example script showing how to use the social media uploaders.
"""
import os
import argparse
from typing import Dict, List

from uploaders.facebook import FacebookUploader
from uploaders.instagram import InstagramUploader
from uploaders.tiktok import TikTokUploader
from uploaders.youtube import YouTubeUploader


def load_credentials(platform: str) -> Dict:
    """
    Load credentials for a specific platform from environment variables.

    Args:
        platform: The platform name ('youtube', 'facebook', 'instagram', 'tiktok')

    Returns:
        Dict containing the credentials
    """
    credentials = {}

    if platform == "youtube":
        credentials = {
            "client_id": os.environ.get("YOUTUBE_CLIENT_ID"),
            "client_secret": os.environ.get("YOUTUBE_CLIENT_SECRET"),
            "refresh_token": os.environ.get("YOUTUBE_REFRESH_TOKEN"),
        }
    elif platform == "facebook":
        credentials = {
            "access_token": os.environ.get("FACEBOOK_ACCESS_TOKEN"),
            "page_id": os.environ.get("FACEBOOK_PAGE_ID"),
        }
    elif platform == "instagram":
        credentials = {
            "access_token": os.environ.get("INSTAGRAM_ACCESS_TOKEN"),
            "instagram_account_id": os.environ.get("INSTAGRAM_ACCOUNT_ID"),
        }
    elif platform == "tiktok":
        credentials = {
            "client_key": os.environ.get("TIKTOK_CLIENT_KEY"),
            "client_secret": os.environ.get("TIKTOK_CLIENT_SECRET"),
            "access_token": os.environ.get("TIKTOK_ACCESS_TOKEN"),
        }

    return credentials


def upload_to_platform(
    platform: str, video_path: str, title: str, description: str, tags: List[str]
) -> str:
    """
    Upload a video to a specified social media platform.

    Args:
        platform: The platform name ('youtube', 'facebook', 'instagram', 'tiktok')
        video_path: Path to the video file
        title: Video title
        description: Video description
        tags: List of tags/hashtags

    Returns:
        URL or ID of the uploaded video
    """
    credentials = load_credentials(platform)

    if platform == "youtube":
        uploader = YouTubeUploader(credentials=credentials)
        result = uploader.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status="private",  # Start as private for safety
        )
    elif platform == "facebook":
        uploader = FacebookUploader(credentials=credentials)
        result = uploader.upload_video(
            video_path=video_path, title=title, description=description, tags=tags
        )
    elif platform == "instagram":
        uploader = InstagramUploader(credentials=credentials)
        result = uploader.upload_video(
            video_path=video_path, title=title, description=description, tags=tags
        )
    elif platform == "tiktok":
        uploader = TikTokUploader(credentials=credentials)
        result = uploader.upload_video(
            video_path=video_path, title=title, description=description, tags=tags
        )
    else:
        return f"Unsupported platform: {platform}"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Upload videos to social media platforms"
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=["youtube", "facebook", "instagram", "tiktok"],
        help="Social media platform to upload to",
    )
    parser.add_argument("--video", required=True, help="Path to the video file")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--description", required=True, help="Video description")
    parser.add_argument(
        "--tags", help="Comma-separated list of tags (no spaces, no # symbols)"
    )

    args = parser.parse_args()

    # Convert tags string to list
    tags_list = []
    if args.tags:
        tags_list = args.tags.split(",")

    # Upload the video
    result = upload_to_platform(
        platform=args.platform,
        video_path=args.video,
        title=args.title,
        description=args.description,
        tags=tags_list,
    )
    print(f"Upload result: {result}")


if __name__ == "__main__":
    main()
