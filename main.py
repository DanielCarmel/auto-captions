#!/usr/bin/env python3
"""
main.py - Main script for processing videos with transcripts, converting text to speech,
and generating styled subtitles
"""

import argparse
import logging
import os
import tempfile
import subprocess

from subtitles_generator import SubtitlesGenerator
from text_to_speech import TextToSpeechGenerator
from video_processor import VideoProcessor
from whisper_align import WhisperAligner

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert text to speech, create captions, and burn them into a video.")
    parser.add_argument("--text-file", required=True, help="Input text file to convert to speech")
    parser.add_argument("--video", required=True, help="Input video file path")
    parser.add_argument("--output", default="output.mp4", help="Output video file path")
    parser.add_argument("--style", default="style_config.json", help="Subtitle style configuration file")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large)")

    return parser.parse_args()


def main():
    """Main entry point of the program."""
    args = parse_arguments()

    # Validate input files
    if not os.path.exists(args.text_file):
        logger.error(f"Text file not found: {args.text_file}")
        return 1

    if not os.path.exists(args.video):
        logger.error(f"Input video file not found: {args.video}")
        return 1

    # Read text file
    try:
        with open(args.text_file, "r", encoding="utf-8") as f:
            text_content = f.read().strip()
            logger.info(f"Read {len(text_content)} characters from {args.text_file}")
    except Exception as e:
        logger.error(f"Error reading text file: {str(e)}")
        return 1

    if not text_content:
        logger.error("Text content is empty")
        return 1

    # Convert text to speech
    logger.info(f"Processing text with {len(text_content)} characters")
    tts_generator = TextToSpeechGenerator()

    try:
        # Generate speech from text
        temp_audio_path = tts_generator.generate_speech(text=text_content)
        logger.info(f"Speech generated: {temp_audio_path}")

        # Create a temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary transcript file
            temp_transcript_path = os.path.join(temp_dir, "transcript.txt")
            with open(temp_transcript_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            # Get speech duration
            video_processor = VideoProcessor()
            speech_duration = video_processor.get_media_duration(temp_audio_path)
            logger.info(f"Speech duration: {speech_duration} seconds")

            # Adjust input video duration to match speech duration
            temp_video_path = os.path.join(temp_dir, "adjusted_video.mp4")
            video_processor.adjust_video_duration(args.video, speech_duration + 2, temp_video_path)
            logger.info(f"Video duration adjusted to match speech duration: {speech_duration} seconds")

            # Create a video with both the original video and the speech audio
            video_with_speech_path = os.path.join(temp_dir, "video_with_speech.mp4")
            ffmpeg_cmd = [
                "ffmpeg", "-i", temp_video_path, "-i", temp_audio_path,
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a",
                "aac", "-shortest", video_with_speech_path, "-y"
            ]

            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"Video with speech created: {video_with_speech_path}")

            # Use WhisperAligner to align the text with the audio
            aligner = WhisperAligner(model_name=args.model)
            aligned_transcript = aligner.align_transcript(
                video_path=video_with_speech_path, transcript_path=temp_transcript_path
            )
            logger.info(f"Transcript aligned with {len(aligned_transcript)} segments")

            # Create subtitle file
            temp_subtitle_path = os.path.join(temp_dir, "subtitles.ass")
            subtitle_generator = SubtitlesGenerator(style_path=args.style)
            subtitle_generator.generate(aligned_transcript=aligned_transcript, output_path=temp_subtitle_path)
            logger.info(f"Subtitles generated: {temp_subtitle_path}")

            # Burn subtitles into video
            video_processor.burn_subtitles(video_path=video_with_speech_path, subtitle_path=temp_subtitle_path,
                                           output_path=args.output)
            logger.info(f"Subtitles burned into video: {args.output}")

        # Clean up temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        logger.info("Processing complete!")
        return 0

    except Exception as e:
        logger.error(f"Error in processing: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
