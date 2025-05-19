#!/usr/bin/env python3
"""
run.py - Main script to run examples from the examples directory
"""

import argparse
import json
import logging
import os
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define paths
EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(EXAMPLES_DIR, "examples.json")


def load_examples_config():
    """Load the examples configuration from examples.json"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading examples configuration: {str(e)}")
        sys.exit(1)


def list_examples(config):
    """List all available examples"""
    print("\nAvailable Examples:\n")

    for idx, example in enumerate(config["examples"], 1):
        print(f"{idx}. {example['title']}")
        print(f"   Description: {example['description']}")
        print(f"   Script: {example['main_script']}")
        print("")

    print("\nRun an example with: python run.py --run <example_name>")
    print("For more details about an example: python run.py --info <example_name>\n")


def show_example_info(config, example_name):
    """Show detailed information about a specific example"""
    for example in config["examples"]:
        if example["name"] == example_name:
            print(f"\nExample: {example['title']}")
            print(f"Description: {example['description']}")
            print(f"Main Script: {example['main_script']}")

            print("\nInput Files:")
            for input_file in example["input_files"]:
                print(f"  - {input_file}")

            print("\nOutput Files:")
            for output_file in example["output_files"]:
                print(f"  - {output_file}")

            print(f"\nDocumentation: {example['documentation']}")

            # Check if documentation file exists and display its content
            doc_path = os.path.join(EXAMPLES_DIR, example["documentation"])
            if os.path.exists(doc_path):
                print("\nDocumentation Preview:")
                with open(doc_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    preview = "".join(lines[:15])
                    print(f"\n{preview}...\n")
                print(f"See full documentation at: {doc_path}")

            return True

    print(f"Example '{example_name}' not found.")
    return False


def run_example(config, example_name):
    """Run a specific example"""
    for example in config["examples"]:
        if example["name"] == example_name:
            script_path = os.path.join(EXAMPLES_DIR, example["main_script"])

            print(f"\nRunning Example: {example['title']}")
            print(f"Description: {example['description']}")
            print(f"Script: {script_path}\n")

            # Check if the script exists
            if not os.path.exists(script_path):
                logger.error(f"Script not found: {script_path}")
                return False

            # Make sure the script is executable
            try:
                os.chmod(script_path, 0o755)
            except Exception as e:
                logger.warning(f"Could not make script executable: {str(e)}")

            # Run the script
            try:
                result = subprocess.run(
                    [sys.executable, script_path], cwd=EXAMPLES_DIR, check=True
                )

                print(f"\nExample '{example_name}' completed successfully!")

                # Check if output files were generated
                all_exist = True
                print("\nOutput Files:")
                for output_file in example["output_files"]:
                    output_path = os.path.join(EXAMPLES_DIR, output_file)
                    if os.path.exists(output_path):
                        print(f"  - ✓ {output_file}")
                    else:
                        print(f"  - ✗ {output_file} (not found)")
                        all_exist = False

                if all_exist:
                    print("\nAll expected output files were generated.")
                else:
                    print("\nSome expected output files were not generated.")

                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Error running example: {str(e)}")
                return False

    print(f"Example '{example_name}' not found.")
    return False


def run_all_examples(config):
    """Run all examples in the configuration"""
    print("\nRunning All Examples")
    print("===================\n")

    success = 0
    failed = 0

    for example in config["examples"]:
        print(f"\n[{example['name']}] Running Example: {example['title']}")

        script_path = os.path.join(EXAMPLES_DIR, example["main_script"])

        # Check if the script exists
        if not os.path.exists(script_path):
            logger.error(f"Script not found: {script_path}")
            failed += 1
            continue

        # Make sure the script is executable
        try:
            os.chmod(script_path, 0o755)
        except Exception as e:
            logger.warning(f"Could not make script executable: {str(e)}")

        # Run the script
        try:
            result = subprocess.run(
                [sys.executable, script_path], cwd=EXAMPLES_DIR, check=True
            )

            print(f"[{example['name']}] Example completed successfully!")
            success += 1
        except subprocess.CalledProcessError as e:
            logger.error(f"[{example['name']}] Error running example: {str(e)}")
            failed += 1

    print(f"\nExamples completed. {success} succeeded, {failed} failed.")
    return success > 0 and failed == 0


def check_dependencies(config):
    """Check if all required dependencies are installed"""
    print("\nChecking Dependencies")
    print("====================\n")

    # Check Python packages
    missing_packages = []
    for dependency in config.get("dependencies", []):
        # Extract package name (without version)
        package_name = dependency.split(">=")[0].split("==")[0].strip()

        try:
            __import__(package_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            missing_packages.append(dependency)
            print(f"✗ {package_name} is not installed")

    # Check system requirements
    missing_system_reqs = []
    for req in config.get("system_requirements", []):
        try:
            subprocess.run(
                ["which", req],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            print(f"✓ {req} is available in PATH")
        except subprocess.CalledProcessError:
            missing_system_reqs.append(req)
            print(f"✗ {req} is not available in PATH")

    if missing_packages or missing_system_reqs:
        print("\nMissing Dependencies:")

        if missing_packages:
            print("\nPython Packages:")
            print("pip install " + " ".join(missing_packages))

        if missing_system_reqs:
            print("\nSystem Requirements:")
            print("Please install: " + ", ".join(missing_system_reqs))

        return False

    print("\nAll dependencies are satisfied!")
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run Audo-Captions examples")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--list", action="store_true", help="List all available examples"
    )
    group.add_argument("--run", metavar="EXAMPLE", help="Run a specific example")
    group.add_argument("--run-all", action="store_true", help="Run all examples")
    group.add_argument(
        "--info", metavar="EXAMPLE", help="Show information about a specific example"
    )
    group.add_argument(
        "--check", action="store_true", help="Check if all dependencies are installed"
    )

    args = parser.parse_args()

    # Load examples configuration
    config = load_examples_config()

    if args.list:
        list_examples(config)
    elif args.run:
        success = run_example(config, args.run)
        sys.exit(0 if success else 1)
    elif args.run_all:
        success = run_all_examples(config)
        sys.exit(0 if success else 1)
    elif args.info:
        found = show_example_info(config, args.info)
        sys.exit(0 if found else 1)
    elif args.check:
        success = check_dependencies(config)
        sys.exit(0 if success else 1)
    else:
        # Default behavior: list available examples
        list_examples(config)


if __name__ == "__main__":
    main()
