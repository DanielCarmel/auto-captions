#!/usr/bin/env python3
"""
adjust_subtitles.py - Tool for manually adjusting subtitle timings
"""

import argparse
import logging

import pysubs2

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Adjust subtitle timings")
    parser.add_argument("--input", required=True, help="Input .ass subtitle file")
    parser.add_argument(
        "--output", help="Output subtitle file (default: overwrite input)"
    )
    parser.add_argument(
        "--shift",
        type=float,
        default=0,
        help="Shift all subtitles by N seconds (can be negative)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Scale subtitle durations by this factor",
    )
    parser.add_argument(
        "--stretch", type=float, default=1.0, help="Stretch or compress all timings"
    )
    parser.add_argument(
        "--split", action="store_true", help="Split long subtitles into multiple lines"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=42,
        help="Maximum characters per line when splitting",
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=1.0,
        help="Minimum duration for subtitles in seconds",
    )
    return parser.parse_args()


def load_subtitles(subtitle_path):
    """Load subtitle file."""
    try:
        return pysubs2.load(subtitle_path)
    except Exception as e:
        logger.error(f"Error loading subtitle file: {str(e)}")
        raise


def shift_subtitles(subs, shift_seconds):
    """Shift all subtitles by the specified number of seconds."""
    if shift_seconds == 0:
        return

    shift_ms = int(shift_seconds * 1000)
    logger.info(f"Shifting subtitles by {shift_seconds} seconds ({shift_ms} ms)")

    for event in subs.events:
        event.start += shift_ms
        event.end += shift_ms


def scale_durations(subs, scale_factor):
    """Scale the duration of each subtitle."""
    if scale_factor == 1.0:
        return

    logger.info(f"Scaling subtitle durations by factor of {scale_factor}")

    for event in subs.events:
        duration = event.end - event.start
        new_duration = int(duration * scale_factor)
        event.end = event.start + new_duration


def stretch_timings(subs, stretch_factor):
    """Stretch or compress all subtitle timings."""
    if stretch_factor == 1.0:
        return

    logger.info(f"Stretching subtitle timings by factor of {stretch_factor}")

    for event in subs.events:
        event.start = int(event.start * stretch_factor)
        event.end = int(event.end * stretch_factor)


def enforce_min_duration(subs, min_duration_sec):
    """Ensure all subtitles have a minimum duration."""
    min_duration_ms = int(min_duration_sec * 1000)

    adjustments = 0
    for event in subs.events:
        duration = event.end - event.start
        if duration < min_duration_ms:
            event.end = event.start + min_duration_ms
            adjustments += 1

    if adjustments > 0:
        logger.info(
            f"Adjusted {adjustments} subtitles to have minimum duration of {min_duration_sec} seconds"
        )


def split_long_subtitles(subs, max_length):
    """Split long subtitles into multiple lines."""
    if max_length <= 0:
        return

    logger.info(f"Splitting subtitles longer than {max_length} characters")

    new_events = []
    removed_events = []

    for event in subs.events:
        if len(event.text) <= max_length:
            continue

        # Simple split at space character closest to the middle
        words = event.text.split()

        if len(words) <= 1:
            continue  # Can't split single words

        # Find best split point
        current_line = ""
        lines = []
        for word in words:
            if (
                len(current_line) + len(word) + 1 > max_length and current_line
            ):  # +1 for space
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word

        if current_line:
            lines.append(current_line)

        if len(lines) <= 1:
            continue

        # Create new subtitle events
        removed_events.append(event)
        duration = event.end - event.start
        segment_duration = duration / len(lines)

        for i, line in enumerate(lines):
            new_event = event.copy()
            new_event.text = line
            new_event.start = event.start + int(i * segment_duration)
            new_event.end = event.start + int((i + 1) * segment_duration)
            new_events.append(new_event)

    # Remove original events and add split ones
    for event in removed_events:
        subs.events.remove(event)

    subs.events.extend(new_events)

    # Sort events by start time
    subs.events.sort(key=lambda event: event.start)

    if new_events:
        logger.info(
            f"Split {len(removed_events)} subtitles into {len(new_events)} new subtitles"
        )


def main():
    """Main entry point of the program."""
    args = parse_arguments()

    # Load subtitle file
    subtitle_path = args.input
    output_path = args.output or subtitle_path

    logger.info(f"Loading subtitle file: {subtitle_path}")
    subs = load_subtitles(subtitle_path)

    # Apply requested adjustments
    shift_subtitles(subs, args.shift)
    scale_durations(subs, args.scale)
    stretch_timings(subs, args.stretch)
    enforce_min_duration(subs, args.min_duration)

    if args.split:
        split_long_subtitles(subs, args.max_length)

    # Save adjusted subtitles
    logger.info(f"Saving adjusted subtitles to: {output_path}")
    subs.save(output_path)
    logger.info("Subtitle adjustment complete!")


if __name__ == "__main__":
    main()
