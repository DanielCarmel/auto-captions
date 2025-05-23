"""
subtitles_generator.py - Generates styled ASS subtitles from transcript with timestamps
"""

import json
import logging
from pathlib import Path
from typing import List

import pysubs2

from media_processors.whisper_align import Segment

logger = logging.getLogger(__name__)

# Default subtitle style configuration
DEFAULT_STYLE = {
    "font_name": "Arial",
    "font_size": 36,
    "primary_color": "&H00FFFFFF",  # White
    "outline_color": "&H000000FF",  # Black
    "back_color": "&H80000000",     # Semi-transparent background
    "bold": True,
    "italic": False,
    "underline": False,
    "strike_out": False,
    "alignment": 2,             # Centered
    "margin_v": 50,             # Vertical margin
    "margin_l": 20,             # Left margin
    "margin_r": 20,             # Right margin
    "border_style": 1,          # Outline + drop shadow
    "outline": 2.0,             # Outline thickness
    "shadow": 2.0               # Shadow distance
}


class SubtitlesGenerator:
    """Generates styled .ass subtitles from aligned transcript segments."""

    def __init__(self, style_path: str = None):
        """
        Initialize the SubtitlesGenerator.

        Args:
            style_path: Path to the subtitle style configuration JSON file
        """
        # If style_path is provided and file exists, load it
        if style_path and Path(style_path).exists():
            self._load_style_config(style_path)
            logger.info(f"Loaded custom style from {style_path}")
        else:
            # Use default style only when file doesn't exist
            self.style_config = DEFAULT_STYLE.copy()
            if style_path:
                logger.warning(f"Style file not found: {style_path}. Using default style.")
            else:
                logger.info("No style path provided. Using default style.")

        logger.info("Initialized SubtitlesGenerator with style config")

    def _load_style_config(self, style_path: str):
        """
        Load custom style configuration from JSON file.

        Args:
            style_path: Path to the style configuration file
        """
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                custom_style = json.load(f)

            # Update default style with custom settings
            self.style_config = DEFAULT_STYLE.copy()
            self.style_config.update(custom_style)
            logger.info(f"Loaded custom style from {style_path}")

        except Exception as e:
            logger.error(f"Error loading style config from {style_path}: {str(e)}")
            logger.warning("Using default style configuration")
            self.style_config = DEFAULT_STYLE.copy()

    def _create_style(self, subs: pysubs2.SSAFile) -> str:
        """
        Create a subtitle style in the SSA file.

        Args:
            subs: The SSA file object

        Returns:
            The name of the created style
        """
        style_name = "DefaultStyle"

        # Create style object
        style = pysubs2.SSAStyle(
            fontname=self.style_config["font_name"],
            fontsize=self.style_config["font_size"],
            primarycolor=self.style_config["primary_color"],
            outlinecolor=self.style_config["outline_color"],
            backcolor=self.style_config["back_color"],
            bold=self.style_config["bold"],
            italic=self.style_config["italic"],
            underline=self.style_config["underline"],
            strikeout=self.style_config["strike_out"],
            alignment=self.style_config["alignment"],
            marginv=self.style_config["margin_v"],
            marginl=self.style_config["margin_l"],
            marginr=self.style_config["margin_r"],
            borderstyle=self.style_config["border_style"],
            outline=self.style_config["outline"],
            shadow=self.style_config["shadow"],
        )

        # Add style to the subtitle file
        subs.styles[style_name] = style

        return style_name

    def generate(self, aligned_transcript: List[Segment], output_path: str, each_word: bool = False):
        """
        Generate ASS subtitle file from aligned transcript segments.

        Args:
            aligned_transcript: List of aligned transcript segments
            output_path: Output subtitle file path
            each_word: If True, generate timestamps for each word instead of segments
        """
        logger.info(f"Generating ASS subtitles with {len(aligned_transcript)} segments, each_word={each_word}")

        # Create a new subtitle file
        subs = pysubs2.SSAFile()

        # Set up the style
        style_name = self._create_style(subs)

        if not each_word:
            # Standard mode: Add events (subtitle lines) from aligned transcript
            for segment in aligned_transcript:
                start_time = int(segment.start * 1000)  # Convert to milliseconds
                end_time = int(segment.end * 1000)  # Convert to milliseconds

                # Create subtitle event
                event = pysubs2.SSAEvent(start=start_time, end=end_time, text=segment.text, style=style_name)

                # Add event to subtitle file
                subs.events.append(event)
        else:
            # Word-by-word mode
            for segment in aligned_transcript:
                # Get segment duration in milliseconds
                segment_start_ms = int(segment.start * 1000)
                segment_end_ms = int(segment.end * 1000)
                segment_duration = segment_end_ms - segment_start_ms

                # Split segment text into words
                words = segment.text.split()
                if not words:
                    continue

                # Calculate time per word (approximate distribution)
                word_duration = segment_duration / len(words)

                # Create a subtitle event for each word
                for i, word in enumerate(words):
                    word_start = segment_start_ms + int(i * word_duration)
                    word_end = segment_start_ms + int((i + 1) * word_duration)

                    # Ensure last word ends exactly at segment end
                    if i == len(words) - 1:
                        word_end = segment_end_ms

                    # Create subtitle event
                    event = pysubs2.SSAEvent(start=word_start, end=word_end, text=word, style=style_name)

                    # Add event to subtitle file
                    subs.events.append(event)

        # Save to file
        subs.save(output_path)
        logger.info(f"Subtitles saved to {output_path}")
