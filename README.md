# Auto-Captions

A Python tool that automatically generates styled subtitles for videos using a provided transcript, aligns them with Whisper, and burns them into the video.

## Features

- Extract audio from video files
- Use OpenAI's Whisper to align transcripts with audio timestamps
- Generate styled ASS subtitles with customizable appearance
- Burn subtitles directly into videos using FFmpeg
- Text summarization and processing with local LLMs
- Convert text to speech with automatic captions
- Upload videos to social networks (YouTube, Facebook, Instagram, TikTok)
- Send videos and messages to Telegram channels/chats
- Batch process videos with consistent styling
- Support for local LLM models via llama-cpp-python

## Requirements

- Python 3.8 or higher
- FFmpeg (installed and in PATH)
- Dependencies listed in `requirements.txt`
- Optional: Local LLM models via llama-cpp-python (see [LLM Setup](docs/llama_cpp.md))

## Installation

### Using uv (Recommended)

1. Clone this repository or download the source code
2. Run the setup script which will set up a virtual environment and install dependencies using uv:

```bash
./scripts/setup.sh
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

### Using Social Media Uploaders

To upload your captioned videos to social networks:

1. First, set up your API credentials:

```bash
python -m uploaders.setup_credentials --platform youtube
# Or set up credentials for all platforms
python -m uploaders.setup_credentials --platform all
```

2. Upload a video from the command line:

```bash
python -m uploaders.upload_example --platform youtube \
                                 --video output.mp4 \
                                 --title "My Awesome Video" \
                                 --description "Video with auto-generated captions!" \
                                 --tags audo,captions,demo
```

3. Or use the social media distributor in your code:

```python
from uploaders.social_media_distributor import SocialMediaDistributor

# Initialize with credentials directory
distributor = SocialMediaDistributor(credentials_dir="~/.audo-captions/credentials")

# Upload to multiple platforms
results = distributor.process_and_distribute(
    input_video_path="input.mp4",
    subtitles_path="subtitles.srt",
    output_path="output.mp4",
    platforms=["youtube", "facebook"],
    metadata={
        "title": "My Awesome Video",
        "description": "Video with auto-generated captions!",
        "tags": ["audo", "captions", "demo"]
    }
)
```

For more detailed instructions, see the [Uploaders README](uploaders/README.md).

### Using Telegram Integration

The tool provides capabilities to send videos and text messages to Telegram chats or channels:

1. Set up your Telegram bot and get a bot token from [@BotFather](https://t.me/botfather)

2. Find your chat ID (you can use [@userinfobot](https://t.me/userinfobot))

3. Set environment variables (recommended) or provide them as arguments:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

4. Send a video to Telegram:

```bash
python -m telegram_bot.bot --video output.mp4 --caption "My video with captions"
```

5. Or send a text message:

```bash
python -m telegram_bot.bot --text "Video processing complete!"
```

6. In your own code:

```python
from telegram_bot.bot import send_video_to_telegram, send_text_to_telegram

# Send video
send_video_to_telegram(
    video_path="path/to/video.mp4",
    caption="My awesome video!",
    bot_token="your_bot_token",  # Optional if env var is set
    chat_id="your_chat_id"       # Optional if env var is set
)

# Send text message
send_text_to_telegram(
    text="Processing complete!",
    bot_token="your_bot_token",  # Optional if env var is set
    chat_id="your_chat_id"       # Optional if env var is set
)
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

### Text-to-Speech Services

The tool supports multiple text-to-speech services:

#### Google Text-to-Speech (Default)

```bash
python main.py --video input.mp4 --output output.mp4 --tts google
```

#### AWS Polly

To use AWS Polly (requires AWS credentials to be configured):

```bash
python main.py --video input.mp4 --output output.mp4 --tts aws --aws-voice Joanna --aws-engine neural
```

AWS Polly options:
- `--aws-voice`: Voice ID to use (e.g., Joanna, Matthew, Nicole, Emma, etc.)
- `--aws-engine`: Engine type (standard, neural, or long-form)

Note: AWS credentials must be configured through AWS CLI (`aws configure`) or environment variables.

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

## Using Local LLMs with llama-cpp-python

This project supports using local LLMs through llama-cpp-python instead of requiring Ollama. This gives you more flexibility in how you load and use models.

### Installing llama-cpp-python

You can install llama-cpp-python with varying levels of optimization:

```bash
# Basic installation
pip install llama-cpp-python

# With CPU optimizations (OpenBLAS)
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python

# With CUDA support (for NVIDIA GPUs)
CMAKE_ARGS="-DLLAMA_CUBLAS=ON" pip install llama-cpp-python
```

### Downloading and Managing Models

We've included a helper script to download and manage model files. Models will be stored in `~/models/llama` by default.

```bash
# List available models and supported model IDs
python scripts/setup_models.py list

# Download a specific model (e.g., mistral:7b)
python scripts/setup_models.py download mistral:7b

# Show information about downloaded models
python scripts/setup_models.py info
```

### Configuration

In your code, you can specify which model to use and where to find it:

```python
from ai_text_processor import AITextProcessor

# Initialize with default settings
ai_processor = AITextProcessor(local_model="mistral:7b")

# Or specify a custom models directory
models_dir = "/path/to/your/models"
ai_processor = AITextProcessor(local_model="mistral:7b", models_dir=models_dir)

# Check if model is available and use it
if ai_processor.is_available():
    summary = ai_processor.summarize_text(
        text="Your text here", 
        style="tiktok",
        tone="casual"
    )
```

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
6. **Social Media Distribution**: Optionally uploads the processed videos to various social media platforms.
7. **Telegram Integration**: Sends videos and notification messages to Telegram chats or channels.

## Utilities and Scripts

The project includes several utility scripts:

- `scripts/setup_models.py`: Download and manage LLM models
- `scripts/compare_models.py`: Compare different LLM models for text processing
- `scripts/tts_comparison.py`: Compare different text-to-speech services
- `scripts/setup.sh`: Install dependencies and set up the environment

## License

MIT

## Credits

This tool uses:
- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition and alignment
- [pysubs2](https://github.com/tkarabela/pysubs2) for subtitle generation
- [FFmpeg](https://ffmpeg.org/) for audio extraction and subtitle burning
- [Google Text-to-Speech (gTTS)](https://pypi.org/project/gTTS/) for text-to-speech conversion
- [AWS Polly](https://aws.amazon.com/polly/) for high-quality text-to-speech
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for local LLM inference
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for Telegram integration
