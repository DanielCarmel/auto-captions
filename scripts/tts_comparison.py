"""
TTS Comparison - Comparing Google TTS and AWS Polly
"""
import os
import sys
import logging

# Add parent directory to path to import from main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tts.goolge_translate import TextToSpeechGenerator
from tts.aws_poly import AwsPollyTTS

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Compare Google TTS and AWS Polly voices"""
    # Test phrases that demonstrate differences in pronunciation and intonation
    phrases = [
        "Welcome to the text-to-speech comparison. Let's hear the difference in quality.",
        "Natural language processing has advanced significantly in recent years.",
        "The quick brown fox jumps over the lazy dog. How did that sound?",
        "This is a longer sentence with varying intonation, pauses, and emphasis on different words.",
        "Can you tell the difference between these text-to-speech engines?"
    ]

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "tts_comparison")
    os.makedirs(output_dir, exist_ok=True)

    # Initialize TTS engines
    google_tts = TextToSpeechGenerator()
    aws_joanna = AwsPollyTTS(voice_id="Joanna", engine="neural")
    aws_matthew = AwsPollyTTS(voice_id="Matthew", engine="neural")

    # Generate speech for each phrase
    for i, phrase in enumerate(phrases):
        logger.info(f"Processing phrase {i+1}: {phrase[:30]}...")

        # Generate with Google TTS
        google_output = os.path.join(output_dir, f"phrase{i+1}_google.mp3")
        google_tts.generate_speech(text=phrase, output_path=google_output)

        # Generate with AWS Polly (Joanna)
        joanna_output = os.path.join(output_dir, f"phrase{i+1}_aws_joanna.mp3")
        aws_joanna.generate_speech(text=phrase, output_path=joanna_output)

        # Generate with AWS Polly (Matthew)
        matthew_output = os.path.join(output_dir, f"phrase{i+1}_aws_matthew.mp3")
        aws_matthew.generate_speech(text=phrase, output_path=matthew_output)

    # Create a comparison HTML page to easily listen to the differences
    html_output = os.path.join(output_dir, "comparison.html")
    with open(html_output, 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TTS Comparison: Google TTS vs AWS Polly</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .phrase { margin-bottom: 40px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
                .players { display: flex; flex-wrap: wrap; }
                .player { margin: 10px; flex: 1 0 200px; }
                h1, h2 { color: #333; }
                .text { font-size: 18px; margin-bottom: 20px; padding: 10px; background: #f5f5f5; border-radius: 5px; }
                audio { width: 100%; }
            </style>
        </head>
        <body>
            <h1>Text-to-Speech Comparison</h1>
            <p>This page compares the default Google TTS service with AWS Polly voices.</p>
        """)

        for i, phrase in enumerate(phrases):
            f.write(f"""
            <div class="phrase">
                <h2>Phrase {i+1}</h2>
                <div class="text">{phrase}</div>
                <div class="players">
                    <div class="player">
                        <h3>Google TTS</h3>
                        <audio controls src="phrase{i+1}_google.mp3"></audio>
                    </div>
                    <div class="player">
                        <h3>AWS Polly (Joanna)</h3>
                        <audio controls src="phrase{i+1}_aws_joanna.mp3"></audio>
                    </div>
                    <div class="player">
                        <h3>AWS Polly (Matthew)</h3>
                        <audio controls src="phrase{i+1}_aws_matthew.mp3"></audio>
                    </div>
                </div>
            </div>
            """)

        f.write("""
        </body>
        </html>
        """)

    print(f"\nTTS comparison completed! Audio files saved to {output_dir}")
    print(f"Open {html_output} in a web browser to compare the voices")
    print("Note: AWS credentials must be correctly configured for the AWS Polly examples to work.")


if __name__ == "__main__":
    main()
