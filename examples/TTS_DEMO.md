# Text-to-Speech Feature Demo

This document provides a step-by-step guide on how to use the text-to-speech feature to convert text into captioned videos.

## Prerequisites

Make sure you have installed all the required dependencies:

```bash
# Install dependencies
pip install -r ../requirements.txt
```

Or if you're using uv:

```bash
uv pip install -r ../requirements.txt
```

## Basic Usage

### 1. Direct Text Input

You can directly provide the text to convert to speech:

```bash
cd ..  # Go to the main project directory
python main.py tts --text "This is a demonstration of the text-to-speech feature." --output examples/demo_output.mp4
```

### 2. Text File Input

For longer scripts, you can use a text file:

```bash
# Create a text file with your script
echo "This is the first line of the script.
The second line will appear after the first one is spoken.
Each line will be automatically timed and aligned with the speech." > script.txt

# Process the text file
cd ..  # Go to the main project directory
python main.py tts --text-file examples/script.txt --output examples/script_output.mp4
```

### 3. Custom Styling

You can customize the appearance of your captions:

```bash
# Create a custom style file
cat << EOF > examples/custom_style.json
{
    "font_name": "Arial",
    "font_size": 42,
    "primary_color": "&H0000FFFF",
    "outline_color": "&H000000FF",
    "back_color": "&H80000000",
    "bold": true,
    "italic": false,
    "alignment": 2,
    "margin_v": 30
}
EOF

# Apply the custom style
cd ..  # Go to the main project directory
python main.py tts --text "This text will appear with custom styling." --output examples/styled_output.mp4 --style examples/custom_style.json
```

## Example

Here's a complete example workflow:

```bash
# 1. Create a script file
cat << EOF > examples/presentation.txt
Welcome to our demonstration of the Audo-Captions tool.
This tool makes it easy to create professional-looking videos with captions.
The text-to-speech feature converts written content into spoken words.
Whisper AI aligns the text with the audio for perfect timing.
The styled captions are then burned directly into the video.
EOF

# 2. Create a custom style
cat << EOF > examples/presentation_style.json
{
    "font_name": "Helvetica",
    "font_size": 38,
    "primary_color": "&H00FFFFFF",
    "outline_color": "&H000000FF",
    "back_color": "&H60000000",
    "bold": true,
    "italic": false,
    "alignment": 2,
    "margin_v": 40
}
EOF

# 3. Generate the video with captions
cd ..  # Go to the main project directory
python main.py tts --text-file examples/presentation.txt --output examples/presentation.mp4 --style examples/presentation_style.json

# 4. Play the video
ffplay examples/presentation.mp4
```

## Tips for Best Results

1. **Break Text Into Chunks**: For better pacing, break long paragraphs into shorter sentences.
2. **Add Punctuation**: Add proper punctuation to help the text-to-speech engine with proper pausing and intonation.
3. **Test Different Styles**: Experiment with different font sizes and colors for better visibility.
4. **Adjust Margins**: If captions are too close to the edge, adjust the margin values in your style file.
