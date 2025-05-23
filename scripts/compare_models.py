#!/usr/bin/env python
"""
compare_models.py - Compare different Ollama models for text generation
"""

import argparse
import logging
import time
import sys
from typing import List, Dict, Any
import json

try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# List of models to compare (from smallest to largest)
DEFAULT_MODELS = ["phi3:mini", "gemma:2b", "llama3:8b", "mistral:7b"]

# Default prompt for model comparison
DEFAULT_PROMPT = """
Summarize this Reddit story into a 30-second TikTok script. Use casual tone.
Keep it emotional, engaging, and suspenseful. Make it flow well for voice narration.
Don't include stage directions or formatting - just the script text.

Original story:
I bought my girlfriend a new desk for Christmas. She was very clear that she wanted a specific
desk that cost $450, which was more than I wanted to spend, but it's what she wanted so I bought
it for her. Now, 6 months later, she's decided she actually wants a different style desk and is
demanding that I buy her a new one because 'I'm the one who bought the wrong one in the first place.'
I told her that I got exactly what she asked for and I'm not spending another $400+ on a new desk
because she changed her mind.
"""


def ensure_model_available(model_name: str) -> bool:
    """
    Ensure model is available, pulling it if needed.

    Args:
        model_name: Name of the model to check

    Returns:
        True if model is available, False if it couldn't be pulled
    """
    try:
        models = ollama.list()
        available_models = [model.get("name") for model in models.get("models", [])]

        if model_name not in available_models:
            logger.info(
                f"Model '{model_name}' not found locally, pulling from registry..."
            )
            ollama.pull(model_name)
        return True
    except Exception as e:
        logger.error(f"Error ensuring model availability: {e}")
        return False


def benchmark_model(
    model_name: str, prompt: str, max_tokens: int = 200
) -> Dict[str, Any]:
    """
    Benchmark a model for text generation.

    Args:
        model_name: Name of the model to benchmark
        prompt: Prompt to use for generation
        max_tokens: Maximum tokens to generate

    Returns:
        Dictionary with benchmark results
    """
    result = {
        "model": model_name,
        "success": False,
        "generation_time": None,
        "output": None,
        "token_count": None,
        "tokens_per_second": None,
        "error": None,
    }

    try:
        # Run non-streaming test for accurate timing
        start_time = time.time()
        response = ollama.generate(
            model=model_name, prompt=prompt, options={"num_predict": max_tokens}
        )
        end_time = time.time()

        gen_time = end_time - start_time
        output = response.get("response", "")
        token_count = len(output.split())
        tokens_per_second = token_count / gen_time if gen_time > 0 else 0

        result.update(
            {
                "success": True,
                "generation_time": gen_time,
                "output": output,
                "token_count": token_count,
                "tokens_per_second": tokens_per_second,
            }
        )

    except Exception as e:
        result["error"] = str(e)

    return result


def compare_models(
    models: List[str], prompt: str, max_tokens: int = 200
) -> List[Dict[str, Any]]:
    """
    Compare multiple models on the same prompt.

    Args:
        models: List of model names to compare
        prompt: Prompt to use for generation
        max_tokens: Maximum tokens to generate

    Returns:
        List of benchmark results for each model
    """
    results = []

    for model_name in models:
        if ensure_model_available(model_name):
            logger.info(f"Benchmarking model: {model_name}")

            result = benchmark_model(model_name, prompt, max_tokens)
            results.append(result)

            if result["success"]:
                logger.info(
                    f"Generation time: {result['generation_time']:.2f}s, "
                    f"Tokens/sec: {result['tokens_per_second']:.2f}"
                )
            else:
                logger.error(f"Failed to benchmark model: {result['error']}")

            # Give the system a moment to recover
            time.sleep(1)
        else:
            results.append(
                {
                    "model": model_name,
                    "success": False,
                    "error": "Failed to ensure model availability",
                }
            )

    return results


def display_comparison_table(results: List[Dict[str, Any]]) -> None:
    """
    Display a formatted comparison table of benchmark results.

    Args:
        results: List of benchmark results
    """
    # Sort results by generation time (fastest first)
    sorted_results = sorted(
        [r for r in results if r["success"]], key=lambda x: x["generation_time"]
    )

    print("\n" + "=" * 100)
    print(
        f"{'Model':<15} | {'Time (s)':<10} | {'Tokens':<8} | {'Tokens/s':<10} | {'Output Preview':<50}"
    )
    print("-" * 100)

    for result in sorted_results:
        output_preview = result["output"][:50].replace("\n", " ") + "..."
        print(
            f"{result['model']:<15} | {result['generation_time']:.2f}{'s':<8} | "
            f"{result['token_count']:<8} | {result['tokens_per_second']:.2f}{'  ':<6} | "
            f"{output_preview}"
        )

    print("=" * 100)

    # Display failures if any
    failures = [r for r in results if not r["success"]]
    if failures:
        print("\nFailed models:")
        for failure in failures:
            print(f"- {failure['model']}: {failure['error']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Compare different Ollama models for text generation"
    )
    parser.add_argument("--models", type=str, nargs="+", help="Models to compare")
    parser.add_argument("--prompt", type=str, help="Custom prompt for benchmarking")
    parser.add_argument(
        "--max-tokens", type=int, default=200, help="Maximum tokens to generate"
    )
    parser.add_argument("--output-json", type=str, help="Save results to JSON file")

    args = parser.parse_args()

    if not OLLAMA_AVAILABLE:
        logger.error("Ollama package is not installed. Run: pip install ollama")
        sys.exit(1)

    models = args.models if args.models else DEFAULT_MODELS
    prompt = args.prompt if args.prompt else DEFAULT_PROMPT

    logger.info(f"Comparing {len(models)} models: {', '.join(models)}")

    results = compare_models(models, prompt, args.max_tokens)
    display_comparison_table(results)

    if args.output_json:
        # Clean results for JSON serialization (remove actual output text)
        clean_results = []
        for r in results:
            r_copy = r.copy()
            if r_copy.get("output"):
                r_copy["output"] = (
                    r_copy["output"][:100] + "..."
                    if len(r_copy["output"]) > 100
                    else r_copy["output"]
                )
            clean_results.append(r_copy)

        with open(args.output_json, "w") as f:
            json.dump(clean_results, f, indent=2)
        logger.info(f"Results saved to {args.output_json}")

    # Recommend the best model based on speed and availability
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        fastest_model = min(successful_results, key=lambda x: x["generation_time"])
        logger.info(
            f"\nRecommendation: '{fastest_model['model']}' is the fastest model "
            f"({fastest_model['generation_time']:.2f}s, "
            f"{fastest_model['tokens_per_second']:.2f} tokens/sec)")


if __name__ == "__main__":
    main()
