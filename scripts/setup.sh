#!/usr/bin/env bash
# setup.sh - Install dependencies and set up the project using uv

set -e

echo "Setting up audo-captions project..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies with uv
echo "Installing dependencies..."
uv pip install -e .

# If FFmpeg is not installed, provide instructions
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "WARNING: FFmpeg is not installed or not in your PATH."
    echo "FFmpeg is required for this project to work."
    echo ""
    echo "Install FFmpeg using your package manager:"
    echo "  - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Windows: Install from https://ffmpeg.org/download.html"
    echo ""
fi

echo ""
echo "Setup complete! You can now use the project."
echo ""
echo "Example usage:"
echo "  python main.py --video input.mp4 --transcript transcript.txt --output output.mp4"
echo ""
echo "For more options and information, see the README.md file."
