"""text_to_speech.py - Converts input text to speech audio using a TTS engine"""
import logging
import os
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


class TextToSpeechGenerator:
    """Converts text to speech audio files using different TTS engines."""
    def __init__(self):
        """Initialize the text-to-speech generator."""
        logger.info("Initializing TextToSpeechGenerator")
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required dependencies are installed."""
        try:
            # Check if ffmpeg is available for audio processing
            subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info("ffmpeg is available")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("ffmpeg is not installed or not in PATH")
            raise RuntimeError(
                "ffmpeg is required but not found. Please install ffmpeg and make sure it's in your PATH."
            )

    def generate_speech(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Generate speech audio from text using gTTS.

        Args:
            text: The text to convert to speech
            output_path: Path to save the output audio file (optional)

        Returns:
            Path to the generated audio file
        """
        try:
            from gtts import gTTS
        except ImportError:
            logger.error("gTTS package not found. Install with: pip install gtts")
            raise RuntimeError("Missing required package: gtts")

        logger.info(f"Generating speech for text ({len(text)} chars)")

        # Create a temporary file if output path is not provided
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".mp3")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate speech with gTTS
        try:
            tts = gTTS(text=text, lang="en", slow=False,)
            tts.save(output_path)
            logger.info(f"Speech audio saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise
