"""
main.py - Main script for processing videos with transcripts, converting text to speech,
and generating styled subtitles
"""
import logging
import os
import tempfile
import subprocess

from datasources import reddit
from tts.aws_poly import TextToSpeechGenerator
from media_processors.text_processor import AITextProcessor
# from tts.goolge_translate import TextToSpeechGenerator
from media_processors.subtitles_generator import SubtitlesGenerator
from media_processors.video_processor import VideoProcessor
from media_processors.whisper_align import WhisperAligner
from telegram_bot.bot import send_video_to_telegram
import random


BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
VIDEO_PATH = "assets/videos/birds.mp4"
STYLE_PATH = "assets/config/style_config.json"
OUTPUT_PATH = "assets/output/output.mp4"
SUBREDDITS = [
    "entitledparents",
    "shortstories",         # Original short fiction across genres
    "flashfiction",         # Flash fiction under 1000 words
    "shortscarystories",    # Horror stories under 500 words
    "shortscifistories",    # Short science fiction stories
    "WritingPrompts",       # Writing prompts with user-written responses
    "TrueOffMyChest",       # Personal stories and confessions
    "TwoSentenceStories",   # Complete stories in two sentences
    "makestories",          # Collaborative line-by-line storytelling
    "nosleep",              # Horror stories presented as if real
    "UnresolvedMysteries",  # Thoughtful discussion of real-world mysteries
    "LetsNotMeet",          # Real personal encounters with creepy people
    "self",                 # Text-based subreddit for introspection and essays
    "books",                # Discussions and recommendations on books, often with deep textual engagement
    "literature",           # Classic and modern literature discussions
]

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Get Reddit posts
selected_subreddit = random.choice(SUBREDDITS)
posts = reddit.get_reddit_posts(selected_subreddit, "day", 1)

if not posts:
    logger.error("No posts found.")
    exit(1)

# Get the original text content
title = posts[0]["title"]

# Process the text using AITextProcessor
ai_processor = AITextProcessor("/home/daniel/models/llama/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf")
text_script = ai_processor.summarize_text(
    datasource=reddit.get_datasource_name(),
    text=posts[0]["selftext"],
    style="tiktok",
    tone="casual",
    length=60,
    theme=selected_subreddit)

# Create a temporary directory for processing
with tempfile.TemporaryDirectory() as temp_dir:
    # Select TTS service based on user input
    tts_generator = TextToSpeechGenerator(voice_id="Matthew", engine="neural")

    # Generate speech from text
    audio_path = tts_generator.generate_speech(text=text_script, output_path=f'{temp_dir}/speech.mp3')
    logger.debug(f"Speech generated: {audio_path}")

    # Create a temporary transcript file
    transcript_path = os.path.join(temp_dir, "transcript.txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(text_script)

    # Get speech duration
    video_processor = VideoProcessor()
    speech_duration = video_processor.get_media_duration(audio_path)
    logger.debug(f"Speech duration: {speech_duration} seconds")

    # Adjust input video duration to match speech duration
    video_processor.adjust_video_duration(VIDEO_PATH, speech_duration + 2, f"{temp_dir}/adjusted_video.mp4")
    logger.debug(f"Video duration adjusted to match speech duration: {speech_duration} seconds")

    # Create a video with both the original video and the speech audio
    video_with_speech_path = os.path.join(temp_dir, "video_with_speech.mp4")
    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        f"{temp_dir}/adjusted_video.mp4",
        "-i",
        audio_path,
        "-map",
        "0:v",
        "-map",
        "1:a",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        video_with_speech_path,
        "-y",
    ]

    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.debug(f"Video with speech created: {video_with_speech_path}")

    # Use WhisperAligner to align the text with the audio
    aligner = WhisperAligner(model_name="base")
    aligned_transcript = aligner.align_transcript(video_path=video_with_speech_path, transcript_path=transcript_path)
    logger.debug(f"Transcript aligned with {len(aligned_transcript)} segments")

    # Create subtitle file
    temp_subtitle_path = os.path.join(temp_dir, "subtitles.ass")
    subtitle_generator = SubtitlesGenerator(style_path=STYLE_PATH)
    subtitle_generator.generate(aligned_transcript=aligned_transcript, output_path=temp_subtitle_path, each_word=True)
    logger.debug(f"Subtitles generated: {temp_subtitle_path}")

    # Burn subtitles into video
    video_processor.burn_subtitles(
        video_path=video_with_speech_path,
        subtitle_path=temp_subtitle_path,
        output_path=OUTPUT_PATH)

    logger.debug(f"Subtitles burned into video: {OUTPUT_PATH}")
    logger.info("Processing complete!")

# Send the video to Telegram
if send_video_to_telegram(video_path=OUTPUT_PATH, caption=title, bot_token=BOT_TOKEN, chat_id=CHAT_ID):
    logger.info("Video sent successfully to Telegram.")
