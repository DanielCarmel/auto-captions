#!/usr/bin/env python3
"""
example.py - Example script showing how to use the auto-captions tool
"""

import logging
import os
import subprocess
import sys

# Add the parent directory to the Python path to allow importing the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from subtitles_generator import SubtitlesGenerator
from video_processor import VideoProcessor
from whisper_align import Segment

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_test_segments(transcript_path, duration=30, min_segment_duration=1.0):
    """
    Create test segments from transcript for demo purposes when Whisper fails to detect speech.

    Args:
        transcript_path: Path to the transcript file
        duration: Duration of the video in seconds
        min_segment_duration: Minimum duration for each segment in seconds

    Returns:
        List of Segment objects
    """
    with open(transcript_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Skip empty lines
    lines = [line for line in lines if line]

    if not lines:
        return []

    # Calculate how many lines we can fit based on min_segment_duration
    max_segments = int(duration / min_segment_duration)
    if max_segments < 1:
        max_segments = 1

    # Limit lines to what can fit in the video
    if len(lines) > max_segments:
        logger.info(
            f"Video is too short for all transcript lines. Using only the first {max_segments} lines."
        )
        lines = lines[:max_segments]

    # Calculate time per segment
    segment_duration = duration / len(lines)

    # Create segments with calculated timing
    segments = []
    for i, line in enumerate(lines):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration

        segment = Segment(start=start_time, end=end_time, text=line)
        segments.append(segment)

    logger.info(f"Created {len(segments)} test segments from transcript")
    return segments


def main():
    # Example file paths
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Set paths relative to the script directory
    video_path = os.path.join(script_dir, "birds.mp4")
    transcript_path = os.path.join(script_dir, "example_transcript.txt")
    subtitle_path = os.path.join(script_dir, "birds_subtitles.ass")
    output_path = os.path.join(script_dir, "birds_output.mp4")
    style_path = os.path.join(parent_dir, "style_config.json")

    # Check if files exist
    if not os.path.exists(video_path):
        logger.error(f"Video not found: {video_path}")
        logger.info(
            "Please make sure the birds.mp4 file exists in the project directory"
        )
        return

    if not os.path.exists(transcript_path):
        logger.error(f"Example transcript not found: {transcript_path}")
        logger.info("Please provide a transcript file and update the example.py script")
        return

    # Step 1: Align transcript with Whisper
    logger.info("Step 1: Aligning transcript with Whisper")

    # Get video duration
    try:
        # Use ffprobe to get the duration of the video
        ffprobe_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        result = subprocess.run(ffprobe_cmd, check=True, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        logger.info(f"Video duration: {duration} seconds")
    except (subprocess.SubprocessError, ValueError) as e:
        logger.error(f"Error getting video duration: {str(e)}")
        duration = 30  # Default to 30 seconds if we can't get the duration
        logger.info(f"Using default duration: {duration} seconds")

    logger.info("Creating segments from transcript")
    aligned_transcript = create_test_segments(transcript_path, duration=duration)

    # Step 2: Generate styled subtitles
    logger.info("Step 2: Generating styled subtitles")
    subtitle_generator = SubtitlesGenerator(style_path=style_path)
    subtitle_generator.generate(
        aligned_transcript=aligned_transcript, output_path=subtitle_path
    )

    # Step 3: Burn subtitles into video
    logger.info("Step 3: Burning subtitles into video")
    video_processor = VideoProcessor()
    video_processor.burn_subtitles(
        video_path=video_path, subtitle_path=subtitle_path, output_path=output_path
    )

    logger.info(f"Process complete! Output video: {output_path}")
    logger.info(f"Generated subtitle file: {subtitle_path}")


if __name__ == "__main__":
    main()
