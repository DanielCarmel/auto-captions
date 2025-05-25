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
            # Check GPU availability through llama-cpp-python
            gpu_available = False
            try:
                import llama_cpp
                if hasattr(llama_cpp, 'LLAMA_BACKEND_CUDA'):
                    gpu_available = True
                    logger.info("CUDA backend available for LLaMA model")
            except ImportError:
                logger.warning("CUDA backend not available in llama-cpp-python")

            # Optimized parameters for RTX 4070 GPU
            params = {
                "n_ctx": 8192,            # Context window - full model capacity
                "n_batch": 1024,          # Increased batch size for better throughput
                "n_gpu_layers": 35,       # Explicitly set number of layers on GPU (35 is good for 8B model)
                "verbose": False,         # No verbose output
                "main_gpu": 0,            # Use the primary GPU
                "tensor_split": [1.0],    # Assign all tensors to GPU 0
                "f16_kv": True,           # Use half-precision for key/value cache
                "use_mlock": True,        # Lock memory to prevent swapping
            }

            # Use absolute maximum GPU layers if the user specified -1
            if kwargs.get("n_gpu_layers", 0) == -1 and gpu_available:
                logger.info("Using maximum GPU layers for model acceleration")
                params["n_gpu_layers"] = 35  # Typical layer count for 8B model

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
