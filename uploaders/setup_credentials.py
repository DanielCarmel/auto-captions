"""
Utility script for managing social media API credentials.
This script helps securely store and manage credentials for different social media platforms.
"""

import argparse
import json
import os


def create_credentials_directory() -> str:
    """
    Create a directory for storing credentials if it doesn't exist.

    Returns:
        str: Path to the credentials directory
    """
    # Create credentials directory in user's home directory
    credentials_dir = os.path.expanduser("~/.audo-captions/credentials")
    os.makedirs(credentials_dir, exist_ok=True)

    # Set restrictive permissions
    os.chmod(credentials_dir, 0o700)

    return credentials_dir


def setup_youtube_credentials() -> dict:
    """
    Set up YouTube API credentials.

    Returns:
        dict: Credentials dictionary
    """
    print("\n===== YouTube API Credentials =====")
    print(
        "To use the YouTube API, you need OAuth credentials from Google Cloud Console."
    )
    print("Follow these steps:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project")
    print("3. Enable the YouTube Data API v3")
    print("4. Create OAuth 2.0 credentials")
    print("5. Enter the client ID and secret below\n")

    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()

    # In a real implementation, you would handle OAuth flow to get refresh_token
    # This is just a simplified example
    print(
        "\nNOTE: In a full implementation, an OAuth flow would follow to get the refresh token."
    )
    refresh_token = (
        input("Refresh Token (if you already have one): ").strip() or "DUMMY_REFRESH_TOKEN")

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }


def setup_facebook_credentials() -> dict:
    """
    Set up Facebook API credentials.

    Returns:
        dict: Credentials dictionary
    """
    print("\n===== Facebook API Credentials =====")
    print(
        "To use the Facebook API, you need an access token with appropriate permissions."
    )
    print("Follow these steps:")
    print("1. Go to https://developers.facebook.com/")
    print("2. Create a new app")
    print("3. Add the Pages API to your app")
    print("4. Generate a page access token with publish_video permissions")
    print("5. Enter the access token and page ID below\n")

    access_token = input("Page Access Token: ").strip()
    page_id = input("Page ID: ").strip()

    return {"access_token": access_token, "page_id": page_id}


def setup_instagram_credentials() -> dict:
    """
    Set up Instagram API credentials.

    Returns:
        dict: Credentials dictionary
    """
    print("\n===== Instagram API Credentials =====")
    print("To use the Instagram API, you need:")
    print("1. An Instagram Business or Creator Account")
    print("2. A connected Facebook page")
    print(
        "3. An access token with instagram_basic and instagram_content_publish permissions"
    )
    print("4. Your Instagram account ID\n")

    access_token = input("Access Token: ").strip()
    ig_account_id = input("Instagram Account ID: ").strip()

    return {"access_token": access_token, "instagram_account_id": ig_account_id}


def setup_tiktok_credentials() -> dict:
    """
    Set up TikTok API credentials.

    Returns:
        dict: Credentials dictionary
    """
    print("\n===== TikTok API Credentials =====")
    print("To use the TikTok API, you need developer credentials.")
    print("Follow these steps:")
    print("1. Apply for a TikTok developer account")
    print("2. Create an app on the TikTok developer portal")
    print("3. Get your client key and secret")
    print("4. Complete the OAuth flow to get an access token")
    print("5. Enter the credentials below\n")

    client_key = input("Client Key: ").strip()
    client_secret = input("Client Secret: ").strip()
    access_token = input("Access Token: ").strip()

    return {
        "client_key": client_key,
        "client_secret": client_secret,
        "access_token": access_token,
    }


def save_credentials(platform: str, credentials: dict, credentials_dir: str) -> str:
    """
    Save credentials to a JSON file.

    Args:
        platform: Platform name
        credentials: Credentials dictionary
        credentials_dir: Directory to save credentials in

    Returns:
        str: Path to the saved file
    """
    filename = f"{platform}_credentials.json"
    filepath = os.path.join(credentials_dir, filename)

    with open(filepath, "w") as f:
        json.dump(credentials, f, indent=2)

    # Set restrictive file permissions
    os.chmod(filepath, 0o600)

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Set up social media API credentials")
    parser.add_argument(
        "--platform",
        required=True,
        choices=["youtube", "facebook", "instagram", "tiktok", "all"],
        help="Social media platform to set up credentials for",
    )

    args = parser.parse_args()

    credentials_dir = create_credentials_directory()
    print(f"Credentials will be stored in: {credentials_dir}")

    platforms = (
        ["youtube", "facebook", "instagram", "tiktok"]
        if args.platform == "all"
        else [args.platform]
    )

    for platform in platforms:
        try:
            if platform == "youtube":
                creds = setup_youtube_credentials()
            elif platform == "facebook":
                creds = setup_facebook_credentials()
            elif platform == "instagram":
                creds = setup_instagram_credentials()
            elif platform == "tiktok":
                creds = setup_tiktok_credentials()

            filepath = save_credentials(platform, creds, credentials_dir)
            print(f"✓ {platform.capitalize()} credentials saved to {filepath}")

        except KeyboardInterrupt:
            print(f"\nSetup for {platform} cancelled.")
        except Exception as e:
            print(f"\nError setting up {platform} credentials: {e}")

    print("\nSetup complete! You can now use these credentials with the uploaders.")
    print("Example usage:")
    print("  from uploaders.social_media_distributor import SocialMediaDistributor")
    print(
        f"  distributor = SocialMediaDistributor(credentials_dir='{credentials_dir}')"
    )


if __name__ == "__main__":
    main()
