"""aws_poly.py - Converts input text to speech audio using AWS Polly service"""
import logging
import subprocess
from typing import Optional
import boto3

logger = logging.getLogger(__name__)


class TextToSpeechGenerator:
    """Converts text to speech audio files using AWS Polly service."""

    def __init__(self, voice_id: str = "Joanna", engine: str = "neural"):
        """
        Initialize the AWS Polly text-to-speech generator.

        Args:
            voice_id: The AWS Polly voice to use (default: "Joanna")
            engine: The AWS Polly engine to use (standard, neural, or long-form)
        """
        logger.info(f"Initializing AwsPollyTTS with voice {voice_id} and engine {engine}")
        self.voice_id = voice_id
        self.engine = engine
        self._check_dependencies()
        self.polly_client = boto3.client('polly')

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
        # Generate speech with AWS Polly
        try:
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice_id,
                Engine=self.engine
            )

            # Save the audio stream to the file
            if "AudioStream" in response:
                with open(output_path, 'wb') as file:
                    file.write(response['AudioStream'].read())

            logger.info(f"Speech audio saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating speech with AWS Polly: {str(e)}")
            raise
