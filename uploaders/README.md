# Social Media Uploaders

This module provides simple uploaders for various social media platforms, allowing you to automatically distribute videos to multiple social networks.

## Supported Platforms

- YouTube
- Facebook
- Instagram
- TikTok

## Quick Start

### 1. Set up credentials

First, set up your API credentials for the platforms you want to use:

```bash
# Set up credentials for a specific platform
python -m uploaders.setup_credentials --platform youtube

# Or set up credentials for all platforms
python -m uploaders.setup_credentials --platform all
```

### 2. Upload a video to a single platform

```python
from uploaders.youtube import YouTubeUploader

# Initialize with credentials file
uploader = YouTubeUploader(credentials_file="~/.audo-captions/credentials/youtube_credentials.json")

# Or initialize with credentials dictionary
credentials = {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "refresh_token": "YOUR_REFRESH_TOKEN"
}
uploader = YouTubeUploader(credentials=credentials)

# Authenticate
uploader.authenticate()

# Upload a video
result = uploader.upload_video(
    video_path="assets/output/output_with_captions.mp4",
    title="My Awesome Video",
    description="Check out this amazing video with captions!",
    tags=["audo", "captions", "demo"],
    privacy_status="unlisted"
)

print(f"Video uploaded to: {result}")
```

### 3. Distribute to multiple platforms at once

```python
from uploaders.social_media_distributor import SocialMediaDistributor

# Initialize distributor with credentials directory
distributor = SocialMediaDistributor(credentials_dir="~/.audo-captions/credentials")

# Or set credentials manually
distributor.set_credentials("youtube", youtube_credentials)
distributor.set_credentials("facebook", facebook_credentials)

# Define video metadata
metadata = {
    "title": "My Awesome Video",
    "description": "Check out this amazing video with captions!",
    "tags": ["audo", "captions", "demo"]
}

# Process and distribute to multiple platforms
results = distributor.process_and_distribute(
    input_video_path="assets/videos/video_with_speech.mp4",
    subtitles_path="assets/output/subtitles.srt",
    output_path="assets/output/output_with_captions.mp4",
    platforms=["youtube", "facebook"],
    metadata=metadata,
    platform_options={
        "youtube": {"privacy_status": "unlisted"},
        "facebook": {"scheduled_publish_time": 1716435000}  # Example timestamp
    }
)

# Print results
for platform, result in results.items():
    print(f"{platform}: {result}")
```

### 4. Command-line uploading

You can also use the included command-line tool to upload videos:

```bash
python -m uploaders.upload_example --platform youtube \
                                 --video assets/output/output_with_captions.mp4 \
                                 --title "My Awesome Video" \
                                 --description "Check out this amazing video with captions!" \
                                 --tags audo,captions,demo
```

## API Reference

### Base Uploader

All platform-specific uploaders inherit from the `BaseUploader` class and implement:

- `authenticate()`: Authenticates with the platform API
- `upload_video()`: Uploads a video with metadata

### Platform-Specific Parameters

Each platform supports different parameters:

#### YouTube
- `privacy_status`: "public", "unlisted", or "private"
- `category_id`: YouTube category ID
- `publish_at`: Schedule publish time (ISO 8601)

#### Facebook
- `scheduled_publish_time`: UNIX timestamp for scheduling
- `targeting`: Dict with audience targeting options

#### Instagram
- `location_id`: Instagram location ID
- `carousel_items`: Additional media for carousel posts

#### TikTok
- `sound_id`: TikTok sound ID to use
- `brand_content_type`: Type of branded content

## Notes on Implementation

These uploaders provide a simplified interface to the various social media APIs. In a production environment, you would need to:

1. Implement proper OAuth flows for authentication
2. Add error handling and retry logic
3. Implement rate limiting to comply with API restrictions
4. Add support for thumbnail uploads
5. Add progress monitoring for large uploads

The current implementation is designed to be simple and easy to understand, with placeholders for the actual API calls.
