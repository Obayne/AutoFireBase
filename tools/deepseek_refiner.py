"""
DeepSeek Code Refinement Tool

This tool uses DeepSeek API to analyze and refine Python code in the project.
Supports different refinement modes: optimize, document, refactor, security, and test.
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import requests

RefineMode = Literal["optimize", "document", "refactor", "security", "test", "modernize"]


@dataclass
class RefinementConfig:
    """Configuration for code refinement"""

    api_key: str | None = None
    api_base: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-coder"
    temperature: float = 0.1
    max_tokens: int = 4000


class DeepSeekRefiner:
    """DeepSeek-powered code refinement utility"""

    REFINEMENT_PROMPTS = {
        "optimize": (
            "Optimize this Python code for better performance and efficiency. "
            "Focus on algorithmic improvements, reducing complexity, and memory usage. "
            "Preserve functionality and provide comments explaining optimizations."
        ),
        "document": (
            "Add comprehensive documentation to this Python code. "
            "Include docstrings for all functions/classes, inline comments for complex logic, "
            "and type hints where appropriate. Follow Google/NumPy docstring style."
        ),
        "refactor": (
            "Refactor this Python code to improve readability, maintainability, and follow best practices. "
            "Apply SOLID principles, improve naming, reduce code duplication, and enhance structure. "
            "Preserve all functionality."
        ),
        "security": (
            "Analyze this Python code for security vulnerabilities and improve security. "
            "Address input validation, error handling, secure defaults, and potential exploits. "
            "Add security-focused comments and use secure coding practices."
        ),
        "test": (
            "Generate comprehensive pytest unit tests for this Python code. "
            "Include edge cases, error conditions, and integration scenarios. "
            "Use fixtures, mocks, and parametrize where appropriate."
        ),
        "modernize": (
            "Modernize this Python code to use current Python 3.10+ features. "
            "Use type hints, f-strings, dataclasses, pathlib, match statements, and walrus operator where beneficial. "
            "Improve with modern patterns while preserving functionality."
        ),
    }

    def __init__(self, config: RefinementConfig | None = None):
        """Initialize the refiner with configuration"""
        self.config = config or RefinementConfig()

        # Get API key from environment if not provided
        if not self.config.api_key:
            self.config.api_key = os.environ.get("DEEPSEEK_API_KEY")

        if not self.config.api_key:
            raise ValueError(
                "DeepSeek API key not found. Set DEEPSEEK_API_KEY environment variable "
                "or provide it in RefinementConfig"
            )

    def refine_code(
        self, code: str, mode: RefineMode = "optimize", context: str | None = None
    ) -> dict:
        """
        Refine code using DeepSeek API.

        Args:
            code: Python code to refine
            mode: Refinement mode (optimize, document, refactor, security, test, modernize)
            context: Additional context about the code's purpose

        Returns:
            dict with 'refined_code', 'explanation', and 'success' keys
        """
        if mode not in self.REFINEMENT_PROMPTS:
            raise ValueError(
                f"Invalid mode: {mode}. Choose from {list(self.REFINEMENT_PROMPTS.keys())}"
            )

        # Build the prompt
        prompt = self._build_prompt(code, mode, context)

        # Call DeepSeek API
        try:
            response = self._call_api(prompt)
            return {
                "success": True,
                "refined_code": self._extract_code(response),
                "explanation": self._extract_explanation(response),
                "raw_response": response,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "refined_code": None, "explanation": None}

    def refine_file(
        self,
        file_path: Path,
        mode: RefineMode = "optimize",
        output_path: Path | None = None,
        backup: bool = True,
    ) -> dict:
        """
        Refine a Python file.

        Args:
            file_path: Path to Python file
            mode: Refinement mode
            output_path: Where to save refined code (default: overwrites original)
            backup: Whether to create .bak backup

        Returns:
            Refinement result dictionary
        """
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        if not file_path.suffix == ".py":
            return {"success": False, "error": "Only Python (.py) files supported"}

        # Read original code
        original_code = file_path.read_text(encoding="utf-8")

        # Get context from file path
        context = f"This is from {file_path} in the project"

        # Refine the code
        result = self.refine_code(original_code, mode, context)

        if result["success"] and result["refined_code"]:
            # Create backup if requested
            if backup:
                backup_path = file_path.with_suffix(".py.bak")
                backup_path.write_text(original_code, encoding="utf-8")
                result["backup_path"] = str(backup_path)

            # Write refined code
            target_path = output_path or file_path
            target_path.write_text(result["refined_code"], encoding="utf-8")
            result["output_path"] = str(target_path)

        return result

    def batch_refine(
        self,
        directory: Path,
        mode: RefineMode = "optimize",
        pattern: str = "**/*.py",
        exclude_patterns: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict:
        """
        Batch refine multiple Python files.

        Args:
            directory: Root directory to search
            mode: Refinement mode
            pattern: Glob pattern for files
            exclude_patterns: Patterns to exclude (e.g., ["*test*", "*__init__*"])
            dry_run: If True, only analyze without writing

        Returns:
            Summary of batch refinement
        """
        exclude_patterns = exclude_patterns or []
        files = []

        # Find matching files
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                # Check exclusions
                if any(file_path.match(pattern) for pattern in exclude_patterns):
                    continue
                files.append(file_path)

        results = {
            "total_files": len(files),
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "files": [],
        }

        for file_path in files:
            print(f"Processing: {file_path}")

            if dry_run:
                print(f"  [DRY RUN] Would refine with mode: {mode}")
                results["files"].append({"path": str(file_path), "status": "dry_run"})
                continue

            result = self.refine_file(file_path, mode)
            results["processed"] += 1

            if result["success"]:
                results["succeeded"] += 1
                print("  ✓ Success")
            else:
                results["failed"] += 1
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")

            results["files"].append(
                {
                    "path": str(file_path),
                    "status": "success" if result["success"] else "failed",
                    "error": result.get("error"),
                }
            )

        return results

    def _build_prompt(self, code: str, mode: RefineMode, context: str | None) -> str:
        """Build the refinement prompt"""
        base_instruction = self.REFINEMENT_PROMPTS[mode]

        prompt = f"{base_instruction}\n\n"

        if context:
            prompt += f"Context: {context}\n\n"

        prompt += "Original code:\n```python\n"
        prompt += code
        prompt += "\n```\n\n"
        prompt += (
            "Provide the refined code in a markdown code block, "
            "followed by a brief explanation of the changes made."
        )

        return prompt

    def _call_api(self, prompt: str) -> str:
        """Call DeepSeek API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }

        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert Python developer specializing in code refinement and best practices.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        response = requests.post(
            f"{self.config.api_base}/chat/completions", headers=headers, json=payload, timeout=60
        )

        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"]

    def _extract_code(self, response: str) -> str | None:
        """Extract code from markdown code block"""
        lines = response.split("\n")
        code_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```python") or line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                code_lines.append(line)

        if code_lines:
            return "\n".join(code_lines)

        # Fallback: return entire response if no code block found
        return response

    def _extract_explanation(self, response: str) -> str:
        """Extract explanation from response"""
        # Get text after the code block
        parts = response.split("```")
        if len(parts) >= 3:
            return parts[-1].strip()
        return "No explanation provided"


def main():
    """CLI interface for the refiner"""
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek Code Refinement Tool")
    parser.add_argument("path", type=str, help="File or directory to refine")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["optimize", "document", "refactor", "security", "test", "modernize"],
        default="optimize",
        help="Refinement mode",
    )
    parser.add_argument("--batch", action="store_true", help="Batch process directory")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backups")
    parser.add_argument(
        "--exclude",
        action="append",
        help="Patterns to exclude in batch mode (can be specified multiple times)",
    )
    parser.add_argument("--output", type=str, help="Output file (single file mode)")

    args = parser.parse_args()

    # Initialize refiner
    try:
        refiner = DeepSeekRefiner()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    path = Path(args.path)

    if args.batch:
        if not path.is_dir():
            print(f"Error: {path} is not a directory")
            sys.exit(1)

        print(f"Batch refining Python files in {path}")
        print(f"Mode: {args.mode}")
        print(f"Dry run: {args.dry_run}")
        print()

        results = refiner.batch_refine(
            directory=path, mode=args.mode, exclude_patterns=args.exclude, dry_run=args.dry_run
        )

        print("\n" + "=" * 60)
        print("BATCH REFINEMENT SUMMARY")
        print("=" * 60)
        print(f"Total files: {results['total_files']}")
        print(f"Processed: {results['processed']}")
        print(f"Succeeded: {results['succeeded']}")
        print(f"Failed: {results['failed']}")

    else:
        if not path.is_file():
            print(f"Error: {path} is not a file")
            sys.exit(1)

        print(f"Refining {path}")
        print(f"Mode: {args.mode}")
        print()

        output_path = Path(args.output) if args.output else None
        result = refiner.refine_file(
            file_path=path, mode=args.mode, output_path=output_path, backup=not args.no_backup
        )

        if result["success"]:
            print("✓ Refinement successful!")
            print(f"\nExplanation:\n{result['explanation']}")
            if "backup_path" in result:
                print(f"\nBackup saved to: {result['backup_path']}")
            print(f"Output saved to: {result['output_path']}")
        else:
            print(f"✗ Refinement failed: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
