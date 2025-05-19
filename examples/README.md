# Audo-Captions Examples

This directory contains examples and demonstrations for the Audo-Captions tool.

## Quick Start

The examples can be run using the `run.py` script:

```bash
# List all available examples
./run.py --list

# Run a specific example
./run.py --run video_captioning
./run.py --run text_to_speech

# Run all examples
./run.py --run-all

# Get information about a specific example
./run.py --info video_captioning

# Check if all dependencies are installed
./run.py --check
```

## Examples Organization

The examples are organized into the following directories:

- `video_captioning/`: Examples for generating captions for existing videos
- `text_to_speech/`: Examples for converting text to speech with captions
- `assets/`: Shared assets used by the examples (videos, transcripts, etc.)

Each example directory contains:
- Python scripts that demonstrate specific functionality
- A README.md file with detailed documentation
- Sample input and configuration files

The `examples.json` file defines the structure of all examples and is used by the `run.py` script to execute them.

## Available Examples

### Video Captioning

The `video_captioning/` directory contains examples of how to generate captions for existing videos:

- `example.py`: Demonstrates how to generate captions for an existing video
- Example output: Generated subtitles (.ass) and a video with burned-in captions

### Text-to-Speech

The `text_to_speech/` directory contains examples of how to convert text to speech with captions:

- `example_tts.py`: Demonstrates how to convert text to speech with captions
- Example usages: Direct text input, text file input, custom styling

## Running Examples

- `example_tts.py` - Demonstrates how to convert text to speech with captions
- `test_text.txt` - Sample text file for the text-to-speech example
- `tts_example.mp4` - Output video with synthesized speech and captions
- `TTS_DEMO.md` - Detailed guide for using the text-to-speech feature

### Other Files

- `DEMO.md` - General usage demonstration guide
- `generate_test_video.sh` - Script to generate a test video for examples
- `cli_test.mp4` and `text_file_test.mp4` - Example outputs from the CLI

## Running Individual Examples

### Video Captioning Example

```bash
cd video_captioning
python example.py
```

### Text-to-Speech Example

```bash
cd text_to_speech
python example_tts.py
```

## Using from the Main Directory

You can also run these examples from the main project directory:

```bash
# Run video captioning example
python -m examples.video_captioning.example

# Run text-to-speech example 
python -m examples.text_to_speech.example_tts
```

## Detailed Guides
