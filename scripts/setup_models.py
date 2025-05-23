#!/usr/bin/env python
"""
setup_models.py - Script to manage LLaMa models for the project
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("setup_models")

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from llm.llama_cpp_manager import LlamaCppManager, LLAMACPP_AVAILABLE, MODEL_PATHS
except ImportError:
    logger.error("Failed to import LlamaCppManager. Make sure you're running from the correct directory.")
    sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Setup and manage LLaMa models")
    
    parser.add_argument(
        "--models-dir", 
        default=os.path.expanduser("~/models/llama"),
        help="Directory to store models (default: ~/models/llama)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available models")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download a model")
    download_parser.add_argument(
        "model", 
        choices=list(MODEL_PATHS.keys()) + ["all"], 
        help="Model to download or 'all' for all models"
    )
    download_parser.add_argument(
        "--url", 
        help="Optional URL to download the model from", 
        default=None
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show information about models")
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Create the models directory if it doesn't exist
    os.makedirs(args.models_dir, exist_ok=True)
    
    # Initialize the model manager
    manager = LlamaCppManager(models_dir=args.models_dir)
    
    if not LLAMACPP_AVAILABLE:
        logger.warning("llama-cpp-python is not installed.")
        logger.info(manager.get_installation_help())
    
    # Handle commands
    if args.command == "list":
        available_models = manager.list_available_models()
        if available_models:
            logger.info("Available models:")
            for model in available_models:
                logger.info(f"  - {model}")
        else:
            logger.info("No models found in the models directory.")
            
        logger.info("\nSupported model identifiers:")
        for model_id, filename in MODEL_PATHS.items():
            logger.info(f"  - {model_id}: {filename}")
            
    elif args.command == "download":
        if args.model == "all":
            # Download all models
            success = True
            for model_id in MODEL_PATHS.keys():
                logger.info(f"Downloading {model_id}...")
                if not manager.download_model(model_id):
                    success = False
                    
            if success:
                logger.info("All models downloaded successfully.")
            else:
                logger.warning("Some models failed to download.")
        else:
            # Download a specific model
            if manager.download_model(args.model, args.url):
                logger.info(f"Model {args.model} downloaded successfully.")
            else:
                logger.error(f"Failed to download model {args.model}.")
                return 1
                
    elif args.command == "info":
        logger.info("LLaMa Models Information")
        logger.info("=======================")
        logger.info(f"Models directory: {args.models_dir}")
        
        if LLAMACPP_AVAILABLE:
            logger.info("llama-cpp-python is installed and available.")
        else:
            logger.info("llama-cpp-python is NOT installed.")
            
        available_models = manager.list_available_models()
        logger.info(f"Models found: {len(available_models)}")
        for model in available_models:
            model_path = os.path.join(args.models_dir, model)
            size_mb = Path(model_path).stat().st_size / (1024 * 1024)
            logger.info(f"  - {model} ({size_mb:.1f} MB)")
            
        disk_space = os.statvfs(args.models_dir)
        free_space_gb = (disk_space.f_bavail * disk_space.f_frsize) / (1024**3)
        logger.info(f"Free disk space: {free_space_gb:.1f} GB")
    else:
        logger.info("No command specified. Use --help for usage information.")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
