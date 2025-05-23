# filepath: /home/daniel/projects/audo-captions/telegram_bot/bot.py
"""
telegram_bot.py - Module for sending videos and text messages to Telegram chats
"""
import logging
import os
import asyncio
import subprocess

from telegram import Bot
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Class to handle Telegram bot functionalities"""

    def __init__(self, token: str, chat_id: str = None):
        """
        Initialize the Telegram bot.

        Args:
            token (str): Telegram bot API token
            chat_id (str, optional): Default chat ID to send messages to
        """
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token)

    async def send_video_async(
        self, video_path: str, chat_id: str = None, caption: str = None
    ) -> bool:
        """
        Send video to a Telegram chat asynchronously.

        Args:
            video_path (str): Path to the video file
            chat_id (str, optional): Chat ID to send the video to. Uses default if not provided.
            caption (str, optional): Caption for the video

        Returns:
            bool: True if video was sent successfully, False otherwise
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return False

        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.error("No chat ID provided and no default chat ID set")
            return False

        try:
            with open(video_path, "rb") as video_file:
                await self.bot.send_video(
                    chat_id=target_chat_id,
                    video=video_file,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    read_timeout=60,
                    write_timeout=60,
                )
            logger.info(f"Video sent successfully to chat {target_chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send video: {str(e)}")
            return False

    def send_video(
        self, video_path: str, chat_id: str = None, caption: str = None
    ) -> bool:
        """
        Send video to a Telegram chat (synchronous wrapper).

        Args:
            video_path (str): Path to the video file
            chat_id (str, optional): Chat ID to send the video to. Uses default if not provided.
            caption (str, optional): Caption for the video

        Returns:
            bool: True if video was sent successfully, False otherwise
        """
        return asyncio.run(self.send_video_async(video_path, chat_id, caption))

    async def send_text_async(
        self, text: str, chat_id: str = None, parse_mode: str = ParseMode.MARKDOWN
    ) -> bool:
        """
        Send text message to a Telegram chat asynchronously.

        Args:
            text (str): Text message to send
            chat_id (str, optional): Chat ID to send the message to. Uses default if not provided.
            parse_mode (str, optional): Parse mode for text formatting. Defaults to Markdown.

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.error("No chat ID provided and no default chat ID set")
            return False

        try:
            await self.bot.send_message(
                chat_id=target_chat_id,
                text=text,
                parse_mode=parse_mode,
            )
            logger.info(f"Text message sent successfully to chat {target_chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send text message: {str(e)}")
            return False

    def send_text(
        self, text: str, chat_id: str = None, parse_mode: str = ParseMode.MARKDOWN
    ) -> bool:
        """
        Send text message to a Telegram chat (synchronous wrapper).

        Args:
            text (str): Text message to send
            chat_id (str, optional): Chat ID to send the message to. Uses default if not provided.
            parse_mode (str, optional): Parse mode for text formatting. Defaults to Markdown.

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        return asyncio.run(self.send_text_async(text, chat_id, parse_mode))


def ensure_video_under_size_limit(video_path: str, max_size_mb: float = 50.0) -> str:
    """
    Checks if a video is under the size limit and reduces resolution if needed.

    Args:
        video_path (str): Path to the video file
        max_size_mb (float): Maximum file size in MB (default is 50MB for Telegram)

    Returns:
        str: Path to the video file that's under the size limit (could be original or processed)
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return video_path

    # Check file size
    file_size_bytes = os.path.getsize(video_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    if file_size_mb <= max_size_mb:
        logger.info(f"Video size is {file_size_mb:.2f}MB, under the {max_size_mb}MB limit")
        return video_path

    logger.info(f"Video size is {file_size_mb:.2f}MB, exceeding the {max_size_mb}MB limit. Reducing resolution...")

    # Create a temporary file for the reduced video
    file_dir = os.path.dirname(video_path)
    file_name = os.path.basename(video_path)
    base_name, ext = os.path.splitext(file_name)

    output_path = os.path.join(file_dir, f"{base_name}_reduced{ext}")

    # Try progressively lower resolutions until we get under the size limit
    # Resolutions for different formats:
    # - Portrait (9:16) for TikTok, Instagram Reels, YouTube Shorts
    resolutions = ['1080:1920', '720:1280', '540:960', '360:640']

    for resolution in resolutions:
        try:
            # Try to reduce the video resolution using ffmpeg
            cmd = [
                'ffmpeg', '-y', '-i', video_path,
                '-vf', f'scale={resolution}',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '28',
                '-c:a', 'aac', '-b:a', '128k', output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            # Check if the new file is under the size limit
            new_size_bytes = os.path.getsize(output_path)
            new_size_mb = new_size_bytes / (1024 * 1024)

            if new_size_mb <= max_size_mb:
                logger.info(f"Successfully reduced video to {new_size_mb:.2f}MB with resolution {resolution}")
                return output_path

            logger.info(
                f"Video still too large ({new_size_mb:.2f}MB) after reducing to {resolution}. Trying lower resolution."
            )

        except subprocess.SubprocessError as e:
            logger.error(f"Error reducing video resolution: {str(e)}")
            # If we encounter an error, return the original file
            return video_path

    # If we've tried all resolutions and still can't get under the limit
    if os.path.exists(output_path):
        logger.warning("Could not reduce video below size limit, but returning the smallest version created")
        return output_path

    logger.warning("Failed to reduce video size, returning original")
    return video_path


async def async_send_video_to_telegram(
    video_path: str = "assets/output/output.mp4",
    bot_token: str = None,
    chat_id: str = None,
    caption: str = None,
    max_size_mb: float = 50.0,
) -> bool:
    """
    Send a video to a Telegram chat (async version).

    Args:
        video_path (str): Path to the video file, defaults to 'assets/output/output.mp4'
        bot_token (str, optional): Telegram bot token. If not provided, uses TELEGRAM_BOT_TOKEN env variable.
        chat_id (str, optional): Chat ID to send the video to. If not provided, uses TELEGRAM_CHAT_ID env variable.
        caption (str, optional): Caption for the video
        max_size_mb (float, optional): Maximum file size in MB (default is 50MB for Telegram)

    Returns:
        bool: True if video was sent successfully, False otherwise
    """
    # Get token and chat ID from environment variables if not provided
    token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    target_chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    # Check and possibly reduce video size to meet Telegram's 50MB limit
    video_path = ensure_video_under_size_limit(video_path, max_size_mb)

    if not token:
        logger.error(
            "No Telegram bot token provided. Set TELEGRAM_BOT_TOKEN environment variable "
            "or provide as argument."
        )
        return False

    if not target_chat_id:
        logger.error(
            "No chat ID provided. Set TELEGRAM_CHAT_ID environment variable or provide as argument."
        )
        return False

    # Initialize bot and send video
    bot = TelegramBot(token, target_chat_id)
    # Ensure video is under size limit before sending
    processed_video_path = ensure_video_under_size_limit(video_path)
    return await bot.send_video_async(processed_video_path, target_chat_id, caption)


def send_video_to_telegram(
    video_path: str = "assets/output/output.mp4",
    bot_token: str = None,
    chat_id: str = None,
    caption: str = None,
    max_size_mb: float = 50.0,
) -> bool:
    """
    Send a video to a Telegram chat (synchronous wrapper).

    Args:
        video_path (str): Path to the video file, defaults to 'assets/output/output.mp4'
        bot_token (str, optional): Telegram bot token. If not provided, uses TELEGRAM_BOT_TOKEN env variable.
        chat_id (str, optional): Chat ID to send the video to. If not provided, uses TELEGRAM_CHAT_ID env variable.
        caption (str, optional): Caption for the video
        max_size_mb (float, optional): Maximum file size in MB (default is 50MB for Telegram)

    Returns:
        bool: True if video was sent successfully, False otherwise
    """
    return asyncio.run(async_send_video_to_telegram(
        video_path=video_path,
        bot_token=bot_token,
        chat_id=chat_id,
        caption=caption,
        max_size_mb=max_size_mb,
    ))


async def async_send_text_to_telegram(
    text: str,
    bot_token: str = None,
    chat_id: str = None,
    parse_mode: str = ParseMode.MARKDOWN,
) -> bool:
    """
    Send a text message to a Telegram chat (async version).

    Args:
        text (str): Text message to send
        bot_token (str, optional): Telegram bot token. If not provided, uses TELEGRAM_BOT_TOKEN env variable.
        chat_id (str, optional): Chat ID to send the message to. If not provided, uses TELEGRAM_CHAT_ID env variable.
        parse_mode (str, optional): Parse mode for text formatting. Defaults to Markdown.

    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    # Get token and chat ID from environment variables if not provided
    token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    target_chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    if not token:
        logger.error(
            "No Telegram bot token provided. Set TELEGRAM_BOT_TOKEN environment variable "
            "or provide as argument."
        )
        return False

    if not target_chat_id:
        logger.error(
            "No chat ID provided. Set TELEGRAM_CHAT_ID environment variable or provide as argument."
        )
        return False

    # Initialize bot and send text
    bot = TelegramBot(token, target_chat_id)
    return await bot.send_text_async(text, target_chat_id, parse_mode)


def send_text_to_telegram(
    text: str,
    bot_token: str = None,
    chat_id: str = None,
    parse_mode: str = ParseMode.MARKDOWN,
) -> bool:
    """
    Send a text message to a Telegram chat (synchronous wrapper).

    Args:
        text (str): Text message to send
        bot_token (str, optional): Telegram bot token. If not provided, uses TELEGRAM_BOT_TOKEN env variable.
        chat_id (str, optional): Chat ID to send the message to. If not provided, uses TELEGRAM_CHAT_ID env variable.
        parse_mode (str, optional): Parse mode for text formatting. Defaults to Markdown.

    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    return asyncio.run(async_send_text_to_telegram(
        text=text,
        bot_token=bot_token,
        chat_id=chat_id,
        parse_mode=parse_mode,
    ))


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="Send a message to Telegram")
    parser.add_argument(
        "--video", default=None, help="Path to video file (optional)"
    )
    parser.add_argument(
        "--text", default=None, help="Text message to send (optional)"
    )
    parser.add_argument("--token", help="Telegram bot token")
    parser.add_argument("--chat", help="Telegram chat ID")
    parser.add_argument(
        "--caption", default="New video", help="Caption for the video (if sending video)"
    )
    parser.add_argument(
        "--max-size", type=float, default=50.0,
        help="Maximum file size in MB for videos (default: 50.0)"
    )

    args = parser.parse_args()

    # Check if we have video or text to send
    if args.video:
        success = send_video_to_telegram(
            video_path=args.video,
            bot_token=args.token,
            chat_id=args.chat,
            caption=args.caption,
            max_size_mb=args.max_size,
        )
        print(f"Video send {'successful' if success else 'failed'}")

    if args.text:
        success = send_text_to_telegram(
            text=args.text,
            bot_token=args.token,
            chat_id=args.chat,
        )
        print(f"Text send {'successful' if success else 'failed'}")

    if not args.video and not args.text:
        print("Error: You must specify either --video or --text")
        parser.print_help()
