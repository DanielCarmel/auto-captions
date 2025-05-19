"""
whisper_align.py - Aligns a transcript with audio timestamps using Whisper
"""

import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, List

import whisper

logger = logging.getLogger(__name__)


@dataclass
class Segment:
    """Represents a segment of aligned transcript with timing information."""

    start: float  # Start time in seconds
    end: float  # End time in seconds
    text: str  # Text content


class WhisperAligner:
    """Aligns a transcript with audio using OpenAI's Whisper model."""

    def __init__(self, model_name: str = "base"):
        """
        Initialize the WhisperAligner.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        logger.info(f"Initializing WhisperAligner with model: {model_name}")

    def _load_model(self):
        """Load the Whisper model if not already loaded."""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Model loaded successfully")

    def _extract_audio(self, video_path: str) -> str:
        """
        Extract audio from a video file using ffmpeg.

        Args:
            video_path: Path to the input video file

        Returns:
            Path to the extracted audio file
        """
        logger.info(f"Extracting audio from video: {video_path}")

        # Create a temporary file for the audio
        audio_path = tempfile.mktemp(suffix=".wav")

        # Run ffmpeg to extract audio
        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-q:a",
            "0",
            "-map",
            "a",
            "-vn",
            audio_path,
            "-y",
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Audio extracted to: {audio_path}")
            return audio_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting audio: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to extract audio from {video_path}")

    def _whisper_transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio using Whisper and get word-level timestamps.

        Args:
            audio_path: Path to the audio file

        Returns:
            Whisper transcription result
        """
        logger.info("Transcribing audio with Whisper")
        self._load_model()

        # Transcribe with word-level timestamps
        options = {
            "task": "transcribe",
            # "word_timestamps": True,
            "language": "en",
            "verbose": True,
            # "fp16": False,  # Added to avoid attribute src issues
        }

        # Run transcription
        result = self.model.transcribe(audio_path, **options)

        logger.info(f"Transcription complete: {len(result['segments'])} segments")
        return result

    def align_transcript(self, video_path: str, transcript_path: str) -> List[Segment]:
        """
        Align transcript with audio using Whisper.

        Args:
            video_path: Path to the input video
            transcript_path: Path to the transcript

        Returns:
            List of aligned transcript segments with timing information
        """
        # Extract audio from video
        audio_path = self._extract_audio(video_path)

        # TODO: Add reference to test if generated transcript is correct
        # Read the reference transcript
        # reference_transcript = self.read_transcript(transcript_path)

        try:
            # Transcribe audio with Whisper to get timestamps
            result = self._whisper_transcribe(audio_path)

            # Convert Whisper segments to our segment format
            segments = []
            for s in result["segments"]:
                segment = Segment(
                    start=s["start"], end=s["end"], text=s["text"].strip()
                )
                segments.append(segment)

            logger.info(f"Created {len(segments)} aligned segments")

            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

            return segments

        except Exception as e:
            logger.error(f"Error in alignment process: {str(e)}")
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            raise
