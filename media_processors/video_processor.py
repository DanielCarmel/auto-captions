"""
video_processor.py - Processes video with subtitles using ffmpeg
"""
import logging
import os
import subprocess
import tempfile

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processes video files and burns subtitles into them."""

    def __init__(self):
        """Initialize the VideoProcessor."""
        logger.debug("Initializing VideoProcessor")
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Check if ffmpeg is installed and available."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.debug("ffmpeg is available")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("ffmpeg is not installed or not in PATH")
            raise RuntimeError(
                "ffmpeg is required but not found. Please install ffmpeg and make sure it's in your PATH."
            )

    def _copy_video(self, video_path: str, output_path: str) -> str:
        """Copy a video file."""
        logger.debug(f"Copying video from {video_path} to {output_path}")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Use ffmpeg to copy the video without re-encoding
        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-c",
            "copy",
            output_path,
            "-y",
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.debug(f"Video copied to {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error copying video: {e.stderr}")
            raise RuntimeError(f"Failed to copy video: {str(e)}")

    def _trim_video(self, video_path: str, target_duration: float, output_path: str) -> str:
        """
        Trim a video to the specified duration.

        Args:
            video_path: Path to the input video
            target_duration: Target duration in seconds
            output_path: Path for the output video

        Returns:
            Path to the trimmed video
        """
        logger.debug(f"Trimming video to {target_duration} seconds")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Use ffmpeg to trim the video
        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-t",
            str(target_duration),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            output_path,
            "-y",
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.debug(f"Video trimmed to {target_duration} seconds: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error trimming video: {e.stderr}")
            raise RuntimeError(f"Failed to trim video: {str(e)}")

    def _extend_video(self, video_path: str, target_duration: float, output_path: str) -> str:
        """
        Extend a video to the specified duration by looping the video content.

        Args:
            video_path: Path to the input video
            target_duration: Target duration in seconds
            output_path: Path for the output video

        Returns:
            Path to the extended video
        """
        logger.debug(f"Extending video to {target_duration} seconds")

        # Get original duration
        original_duration = self.get_media_duration(video_path)

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create a temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Calculate how many times we need to loop the video
            loops_needed = int(target_duration / original_duration) + 1
            remaining_duration = target_duration % original_duration

            # Make a copy of the original video to the temporary directory
            local_video_path = os.path.join(temp_dir, "original_video.mp4")
            self._copy_video(video_path, local_video_path)

            try:
                # Create a file list for concatenation
                concat_file = os.path.join(temp_dir, "concat.txt")
                with open(concat_file, "w") as f:
                    # Add the complete loops
                    for _ in range(loops_needed - 1):
                        f.write(f"file '{local_video_path}'\n")

                    # Handle the remaining partial loop if needed
                    if remaining_duration > 0.1:  # Only if we need a significant chunk
                        # Create a trimmed version of the original for the remaining duration
                        trimmed_path = os.path.join(temp_dir, "trimmed.mp4")
                        trim_cmd = [
                            "ffmpeg",
                            "-i",
                            local_video_path,
                            "-t",
                            str(remaining_duration),
                            "-c:v",
                            "libx264",
                            "-c:a",
                            "aac",
                            "-strict",
                            "experimental",
                            trimmed_path,
                            "-y",
                        ]

                        subprocess.run(trim_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        f.write(f"file '{trimmed_path}'\n")
                    else:
                        # Add one more complete copy if the remaining time is too short
                        f.write(f"file '{local_video_path}'\n")

                # Concatenate all the video segments
                concat_cmd = [
                    "ffmpeg",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    concat_file,
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                    "-strict",
                    "experimental",
                    output_path,
                    "-y",
                ]

                subprocess.run(concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.debug(f"Video extended to {target_duration} seconds by looping: {output_path}")
                return output_path

            except subprocess.CalledProcessError as e:
                logger.error(f"Error extending video: {e.stderr}")
                raise RuntimeError(f"Failed to extend video: {str(e)}")

    def get_media_duration(self, video_path: str) -> float:
        """
        Get the duration of a media file using ffprobe(mp3, mp4, wav).

        Args:
            video_path: Path to the video file(mp3, mp4, wav)

        Returns:
            Duration of the video in seconds
        """
        logger.debug(f"Getting duration of video: {video_path}")

        # Use ffprobe to get the duration
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]

        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            duration = float(result.stdout.strip())
            logger.debug(f"Video duration: {duration} seconds")
            return duration
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting video duration: {e.stderr}")
            raise RuntimeError(f"Failed to get video duration: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid duration value: {e}")
            raise RuntimeError(f"Failed to parse video duration: {str(e)}")

    def adjust_video_duration(self, video_path: str, target_duration: float, output_path: str) -> str:
        """
        Adjust the duration of a video to match the target duration.
        The video will be trimmed or extended as needed.

        Args:
            video_path: Path to the input video
            target_duration: Target duration in seconds
            output_path: Path for the output video

        Returns:
            Path to the adjusted video
        """
        # Get the current duration of the video
        current_duration = self.get_media_duration(video_path)

        # If durations are close enough, just copy the video
        if abs(current_duration - target_duration) < 0.5:
            logger.debug(f"Video duration ({current_duration}s) already matches target ({target_duration}s)")
            if video_path != output_path:
                self._copy_video(video_path, output_path)
            return output_path

        # Check if we need to trim or extend
        if current_duration > target_duration:
            # Need to trim the video
            return self._trim_video(video_path, target_duration, output_path)
        else:
            # Need to extend the video
            return self._extend_video(video_path, target_duration, output_path)

    def replace_audio(self, video_path: str, audio_path: str, output_path: str) -> str:
        """
        Replace the audio track of a video with a new audio file.

        Args:
            video_path: Path to the input video
            audio_path: Path to the audio file to use
            output_path: Path for the output video with new audio

        Returns:
            Path to the output video with replaced audio
        """
        logger.debug(f"Replacing audio in video {video_path} with {audio_path}")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Prepare ffmpeg command
        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            video_path,
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
            output_path,
            "-y",
        ]

        try:
            # Run ffmpeg command
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.debug(f"Video with replaced audio created: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error replacing audio: {e.stderr}")
            raise RuntimeError(f"Failed to replace audio in video: {str(e)}")

    def burn_subtitles(self, video_path: str, subtitle_path: str, output_path: str):
        """
        Burn subtitles into video using ffmpeg.

        Args:
            video_path: Path to the input video
            subtitle_path: Path to the .ass subtitle file
            output_path: Path for the output video with burned subtitles
        """
        logger.debug(f"Burning subtitles into video: {video_path}")
        logger.debug(f"Using subtitle file: {subtitle_path}")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Prepare ffmpeg command
        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            f"ass={subtitle_path}",
            "-c:a",
            "copy",
            "-c:v",
            "libx264",
            "-crf",
            "18",  # Quality setting (lower is better, 18-28 is good range)
            "-preset",
            "medium",  # Encoding speed/compression tradeoff
            output_path,
            "-y",  # Overwrite output file if it exists
        ]

        try:
            # Run ffmpeg command
            logger.debug("Running ffmpeg to burn subtitles")
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            logger.debug(f"Successfully created video with burned subtitles: {output_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error burning subtitles: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to burn subtitles into video: {str(e)}")
