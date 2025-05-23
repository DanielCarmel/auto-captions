"""
ai_text_processor.py - AI-powered text processing for summarization and content splitting
"""
import logging
from typing import Optional

# Check for llama-cpp-python via our manager
try:
    from llm.llama_cpp_manager import LlamaCppManager, LLAMACPP_AVAILABLE
except ImportError:
    LLAMACPP_AVAILABLE = False

logger = logging.getLogger(__name__)


class AITextProcessor:
    """AI-powered text processor for summarizing and splitting content."""
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the AI text processor.

        Args:
            local_model: Local LLM model name (for llama.cpp)
            models_dir: Directory where models are stored (optional)
            model_path: Direct path to a specific model file (optional)
            config_path: Path to the configuration file (optional)
        """
        if LLAMACPP_AVAILABLE:
            self._llm_manager = LlamaCppManager(model_path=model_path)
        else:
            logger.warning("No local LLM backend available. Install llama-cpp-python.")

    def _speech_seconds_to_max_tokens(self, speech_seconds: float, words_per_minute: int = 150) -> int:
        words_per_second = words_per_minute / 60.0               # Convert to words/sec
        tokens_per_word = 1.33                                   # Approximate GPT: 1 word ≈ 1.33 tokens
        buffer_factor = 1.2
        estimated_tokens = speech_seconds * words_per_second * tokens_per_word * buffer_factor
        return int(estimated_tokens)

    def summarize_text(
        self,
        datasource: str,
        text: str,
        style: str = "tiktok",
        tone: str = "casual",
        length: int = 30,
        theme: Optional[str] = None,
    ) -> str:
        # Calculate maximum tokens based on speech duration
        max_output_tokens = self._speech_seconds_to_max_tokens(length)

        # Calculate approximate word count for prompt clarity (about 150 words per minute)
        word_count_limit = int((length / 60) * 150)

        prompt_parts = [
            f"Summarize this {datasource} story into a {length} seconds {style} script.",
            f"Use {tone} tone.",
            f"IMPORTANT: The script MUST be under {word_count_limit} words to fit in {length} seconds.",
            "Use first-person perspective, casual slang, and short punchy sentences.",
            "Start with phrases that engages the audience",
            "Use modern internet slang where appropriate.",
            "Make it sound like someone's telling a story to their friends.",
            "Do not use hash tags or emojis.",
            "Do not include any additional comments or notes.",
        ]

        if theme:
            prompt_parts.append(f"Make it feel like a {theme} story.")

        prompt_parts.append("THE STORY:")
        prompt_parts.append(text)
        prompt_parts.append("\nSUMMARIZED SCRIPT:")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert TikTok script writer who creates viral-worthy content. "
                    "You specialize in summarizing stories into short, engaging scripts using "
                    "casual slang and creating a cliffhanger ending. "
                    f"CRITICAL: Scripts MUST be under {word_count_limit} words total to fit within {length} seconds. "
                    "Keep it concise, authentic, and emotionally engaging. "
                    "Maintain first-person perspective when appropriate. "
                    "Include internet slang like 'vibin', 'sus', 'lowkey', etc. Make it sound like "
                    "someone casually telling a wild story to their friends, with lots of energy "
                    "and emphasis on surprising or dramatic moments."
                ),
            },
            {"role": "user", "content": "\n".join(prompt_parts)},
        ]

        # Convert the messages list into a properly formatted string for the model
        formatted_prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            formatted_prompt += f"{role.upper()}: {content}\n\n"

        try:
            self._llm_manager.load_model()
            response = self._llm_manager.generate(prompt=formatted_prompt,
                                                  max_tokens=max_output_tokens,
                                                  temperature=0.7,
                                                  top_p=0.9)

            # Format response for better readability
            response = self._format_summarized_text(response)

            return response
        except Exception as e:
            logger.error(f"Error in summarize_text: {e}")
            return None

    def _format_summarized_text(self, text: str) -> str:
        # Clean up the text first - remove any ASSISTANT: prefix that might be included
        if text.upper().startswith("ASSISTANT:"):
            text = text[len("ASSISTANT:"):].strip()

        # Remove any note or comment lines that appear at the end
        note_patterns = [
            r"\n\n\(Note:.*",
            r"\n\nNote:.*",
            r"\n\n\[Note:.*",
            r"\n\n--.*",
            r"\n\nWord count:.*"
        ]

        import re
        for pattern in note_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

        # Enhance emphasis markers if needed
        if '*' not in text:
            # Try to add emphasis to important words
            for word in ['crazy', 'insane', 'wild', 'suddenly', 'shocking', 'unbelievable']:
                if word in text.lower():
                    text = text.replace(word, f"*{word}*")
                    text = text.replace(word.capitalize(), f"*{word.capitalize()}*")

        # Ensure dramatic pauses
        if ',' not in text:
            # Add ellipses for dramatic effect before climactic parts
            for phrase in ['but then', 'suddenly', 'that\'s when', 'and then']:
                if phrase in text.lower():
                    text = text.replace(phrase, f", {phrase}")

        return text.strip()
