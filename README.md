# Auto-Captions

A Python tool that automatically generates styled subtitles for videos using a provided transcript, aligns them with Whisper, and burns them into the video.

## Features

- Extract audio from video files
- Use OpenAI's Whisper to align transcripts with audio timestamps
- Generate styled ASS subtitles with customizable appearance
- Burn subtitles directly into videos using FFmpeg
- Simple command-line interface
- Convert text to speech with automatic captions

## Requirements

- Python 3.8 or higher
- FFmpeg (installed and in PATH)
- Dependencies listed in `requirements.txt`

## Installation

### Using uv (Recommended)

1. Clone this repository or download the source code
2. Run the setup script which will set up a virtual environment and install dependencies using uv:

```bash
./setup.sh
```

### Manual Installation

1. Clone this repository or download the source code
2. Create a virtual environment (recommended)
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:

```bash
python main.py --video input.mp4 --transcript transcript.txt --output output.mp4
```

Advanced options:

```bash
python main.py --video input.mp4 \
               --transcript transcript.txt \
               --output output.mp4 \
               --style custom_style.json \
               --subtitle-output subtitles.ass \
               --model medium
```

### As an installed package

If you've installed the package using the setup script or pip:

```bash
audo-captions --video input.mp4 --transcript transcript.txt --output output.mp4
```

For subtitle adjustments:

```bash
adjust-subtitles --input subtitles.ass --output adjusted.ass --shift -0.5 --scale 1.2
```

## Examples

The `examples` directory contains demonstration files and sample code to help you get started:

- `video_captioning/`: Examples for generating captions for existing videos
- `text_to_speech/`: Examples for converting text to speech with captions
- `assets/`: Shared assets used by the examples

To run the examples:

```bash
# List all available examples
cd examples
./run.py --list

# Run a specific example
./run.py --run video_captioning
./run.py --run text_to_speech

# Run all examples
./run.py --run-all
```

See the `examples/README.md` file for more details.

## Text-to-Speech Feature

The tool also supports converting text to speech with automatic captions. You can provide text directly or through a text file:

### Using Direct Text Input

```bash
python main.py tts --text "This is the text to convert to speech with captions." --output examples/tts_output.mp4
```

### Using a Text File

```bash
python main.py tts --text-file examples/script.txt --output examples/tts_output.mp4
```

### Custom Styling

You can apply custom subtitle styling to the text-to-speech output:

```bash
python main.py tts --text-file examples/script.txt --output examples/tts_output.mp4 --style examples/custom_style.json
```

This feature:
- Converts the input text to speech using Google Text-to-Speech (gTTS)
- Creates a video with the speech audio
- Automatically aligns the text with the audio using Whisper
- Generates styled captions and burns them into the video

This is useful for:
- Creating accessible content with synchronized captions
- Generating instructional videos from scripts
- Producing narrated presentations with subtitles
- Creating content in multiple languages

## Subtitle Styling

Subtitle appearance can be customized via the `style_config.json` file. Available options include:

- Font name and size
- Text color, outline color, and background color
- Bold, italic, underline styling
- Alignment and margins
- Outline and shadow properties

Example style configuration:

```json
{
    "font_name": "Arial",
    "font_size": 36,
    "primary_color": "&H00FFFFFF",
    "outline_color": "&H000000FF",
    "back_color": "&H80000000",
    "bold": true,
    "italic": false,
    "underline": false,
    "strike_out": false,
    "alignment": 2,
    "margin_v": 50,
    "margin_l": 20,
    "margin_r": 20,
    "border_style": 1,
    "outline": 2.0,
    "shadow": 2.0
}
```

## How It Works

1. **Audio Extraction**: The tool first extracts the audio track from the input video.
2. **Transcript Alignment**: Using OpenAI's Whisper, the tool transcribes the audio and aligns the provided transcript with accurate timestamps.
3. **Subtitle Generation**: The aligned transcript segments are converted to Advanced SubStation Alpha (.ass) format with customizable styling.
4. **Subtitle Burning**: FFmpeg is used to embed the subtitles directly into the video file.
5. **Text-to-Speech**: Converts text to speech, aligns it with captions, and generates a video with synchronized subtitles.

## License

MIT

## Credits

This tool uses:
- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition and alignment
- [pysubs2](https://github.com/tkarabela/pysubs2) for subtitle generation
- [FFmpeg](https://ffmpeg.org/) for audio extraction and subtitle burning
- [Google Text-to-Speech (gTTS)](https://pypi.org/project/gTTS/) for text-to-speech conversion
# auto-captions
