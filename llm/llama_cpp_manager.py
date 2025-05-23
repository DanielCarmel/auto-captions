"""
llama_cpp_manager.py - Manager for loading and using LLaMa models via llama-cpp-python
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import llama-cpp-python
try:
    from llama_cpp import Llama

    LLAMACPP_AVAILABLE = True
    LLAMACPP_IMPORT_ERROR = None
except ImportError as e:
    LLAMACPP_AVAILABLE = False
    LLAMACPP_IMPORT_ERROR = str(e)
    logger.warning(f"llama-cpp-python not installed: {e}. \
                   Install with: pip install llama-cpp-python")


class LlamaCppManager:
    """Manager for loading and using LLaMa models via llama-cpp-python."""
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the LLaMa CPP Manager.

        Args:
            model_path: Direct path to a specific model file (optional)
        """
        self._direct_model_path = model_path
        self._loaded_model: Llama = None

    def load_model(self, **kwargs):
        """
        Load a LLaMa model.

        Args:
            model_name: Model identifier or "default" to use the direct model path
            **kwargs: Additional arguments to pass to Llama initialization

        Returns:
            Loaded Llama model or None if loading failed
        """
        if not LLAMACPP_AVAILABLE:
            logger.error("Cannot load model: llama-cpp-python not installed")
            logger.info(self.get_installation_help())

        if not os.path.isfile(self._direct_model_path):
            logger.error(f"Model file not found: {self._direct_model_path}")

        try:
            params = {
                "n_ctx": 4096,  # Context window
                "n_batch": 512,  # Batch size
                "n_gpu_layers": -1,  # Use GPU if available
                "verbose": False,
            }

            # Update with user-provided params
            params.update(kwargs)

            logger.info(f"Loading model from {self._direct_model_path}")
            self._loaded_model = Llama(model_path=self._direct_model_path, **params)
            logger.info(f"Model {self._loaded_model.model_path} loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model {self._loaded_model.model_path}: {str(e)}")

    def generate(
        self,
        prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs,
    ) -> str:
        """
        Generate text using a LLaMa model.

        Args:
            model_name: Model identifier (default "default" which uses the direct model path if provided)
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional parameters for model.generate

        Returns:
            Generated text
        """
        try:
            # Set up generation parameters
            params = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": kwargs.pop("stop", []),
            }
            params.update(kwargs)

            # Generate response
            output = self._loaded_model.create_completion(prompt=prompt, **params)

            # Extract text from response
            if isinstance(output, dict) and "choices" in output:
                response_text = output["choices"][0]["text"]
            else:
                response_text = str(output)

            return response_text.strip()

        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            return ""
