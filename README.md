# Audo-Captions

An automated pipeline for generating captioned videos from online text sources with AI-enhanced processing and distribution to social media platforms.

## Overview

Audo-Captions converts text content from online sources (currently Reddit) into engaging videos with synchronized, styled captions. The pipeline handles everything from content retrieval to distribution:

1. Collects text content from subreddits
2. Processes and enhances the text using AI/LLM
3. Converts text to speech using high-quality TTS engines
4. Aligns the transcript with audio using Whisper
5. Generates styled subtitles
6. Burns subtitles onto background videos
7. Distributes to social media platforms (Telegram, with support for YouTube, TikTok, Instagram, and Facebook)

## Features

- **Content Collection**: Retrieves text from various subreddits
- **AI Text Processing**: Summarizes and adapts content for different platforms using LLama models
- **Text-to-Speech**: Converts text to natural-sounding speech using AWS Polly (with Google TTS support)
- **Audio Alignment**: Uses OpenAI's Whisper to perfectly align text with audio
- **Styled Subtitles**: Generates visually appealing subtitles using ASS format
- **Video Processing**: Combines subtitles, audio, and background videos 
- **Social Media Distribution**: Sends finished videos to Telegram, with support for other platforms

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/audo-captions.git
cd audo-captions

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup LLM models
python scripts/setup_models.py
```

## Configuration

1. Set up environment variables for API keys:
   ```
   export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   export TELEGRAM_CHAT_ID="your_telegram_chat_id"
   # Add AWS credentials if using AWS Polly
   ```

2. Customize style configurations in `assets/config/style_config.json`

3. Add your own background videos to `assets/videos/`

## Usage

Run the main script to process a random subreddit post:

```bash
python main.py
```

### Customization Options

- Change available subreddits by editing the `SUBREDDITS` list in `main.py`
- Select different TTS voices by modifying the `TextToSpeechGenerator` parameters
- Adjust text processing parameters in the `AITextProcessor` call

## Project Structure

```
├── assets/                  # Media assets
│   ├── config/              # Configuration files
│   ├── output/              # Generated videos
│   └── videos/              # Background videos
├── datasources/             # Data source modules
│   └── reddit.py            # Reddit data collection
├── llm/                     # LLM integration
│   └── llama_cpp_manager.py # LLama model management
├── media_processors/        # Media processing modules
│   ├── subtitles_generator.py # Subtitle generation
│   ├── text_processor.py    # Text processing
│   ├── video_processor.py   # Video processing
│   └── whisper_align.py     # Audio-text alignment
├── scripts/                 # Utility scripts
├── telegram_bot/            # Telegram integration
├── tts/                     # Text-to-speech modules
│   ├── aws_poly.py          # AWS Polly integration
│   └── goolge_translate.py  # Google TTS integration
└── uploaders/               # Social media uploaders
    ├── facebook/
    ├── instagram/
    ├── tiktok/
    └── youtube/
```

## Social Media Distribution

The project includes uploaders for multiple platforms:

- **Telegram**: Currently implemented and working
- **YouTube, TikTok, Instagram, Facebook**: Scaffold available in the `uploaders/` directory

To set up additional platform uploaders, see `uploaders/README.md` and run `uploaders/setup_credentials.py`.

## Dependencies

- FFmpeg (for video processing)
- Python 3.8+
- LLama models
- AWS account (for AWS Polly TTS)
- Telegram Bot API credentials

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
