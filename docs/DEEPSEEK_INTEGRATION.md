# DeepSeek Integration Guide

This guide explains how to use DeepSeek for code refinement in the Autofire project.

## Overview

DeepSeek is integrated into the project in two ways:
1. **IDE Integration** - Via Continue extension for real-time code assistance
2. **Batch Refinement Tool** - Command-line tool for refining Python files

## Setup

### 1. Get DeepSeek API Key

1. Sign up at https://platform.deepseek.com/
2. Navigate to API Keys section
3. Create a new API key

### 2. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:DEEPSEEK_API_KEY = "your-api-key-here"
# To persist across sessions:
[System.Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', 'your-api-key-here', 'User')
```

**Windows (Command Prompt):**
```cmd
set DEEPSEEK_API_KEY=your-api-key-here
# To persist: use System Properties > Environment Variables
```

**Linux/Mac:**
```bash
export DEEPSEEK_API_KEY="your-api-key-here"
# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export DEEPSEEK_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 3. Install Dependencies

```bash
pip install requests
```

## IDE Integration (Continue Extension)

The `.continue/config.json` is already configured with DeepSeek:

```json
{
  "models": [
    {
      "title": "DeepSeek Coder",
      "provider": "openai",
      "model": "deepseek-coder",
      "apiBase": "https://api.deepseek.com/v1",
      "apiKey": "${env:DEEPSEEK_API_KEY}"
    }
  ],
  "tabAutocompleteModel": "DeepSeek Coder"
}
```

### Features

- **Tab Completion**: DeepSeek provides intelligent code completions as you type
- **Chat**: Ask DeepSeek questions about your code
- **Inline Edits**: Request code modifications directly in the editor

## Batch Refinement Tool

The `tools/deepseek_refiner.py` script allows you to refine Python code in bulk.

### Refinement Modes

| Mode | Description |
|------|-------------|
| `optimize` | Improve performance and efficiency |
| `document` | Add comprehensive documentation |
| `refactor` | Improve code structure and maintainability |
| `security` | Fix security vulnerabilities |
| `test` | Generate pytest unit tests |
| `modernize` | Update to Python 3.10+ features |

### Usage Examples

#### Refine a Single File

```bash
# Optimize a single file (creates backup)
python tools/deepseek_refiner.py app/main.py --mode optimize

# Add documentation without backup
python tools/deepseek_refiner.py app/device.py --mode document --no-backup

# Refactor and save to new file
python tools/deepseek_refiner.py app/layout.py --mode refactor --output app/layout_refactored.py
```

#### Batch Refine Directory

```bash
# Dry run to see what would be processed
python tools/deepseek_refiner.py app/ --batch --mode optimize --dry-run

# Refine all Python files in app/ directory
python tools/deepseek_refiner.py app/ --batch --mode document

# Refine with exclusions
python tools/deepseek_refiner.py app/ --batch --mode modernize \
  --exclude "*test*" --exclude "*__init__*"
```

#### Common Workflows

**Document entire project:**
```bash
python tools/deepseek_refiner.py . --batch --mode document \
  --exclude "*test*" --exclude "build/*" --exclude "dist/*"
```

**Security audit:**
```bash
python tools/deepseek_refiner.py backend/ --batch --mode security --dry-run
# Review suggestions, then run without --dry-run
```

**Modernize legacy code:**
```bash
python tools/deepseek_refiner.py legacy_module.py --mode modernize
```

**Generate tests:**
```bash
python tools/deepseek_refiner.py app/device.py --mode test --output tests/test_device.py
```

### Python API Usage

You can also use the refiner programmatically:

```python
from pathlib import Path
from tools.deepseek_refiner import DeepSeekRefiner, RefinementConfig

# Initialize with custom config
config = RefinementConfig(
    api_key="your-key",  # or leave None to use environment variable
    temperature=0.1,
    max_tokens=4000
)
refiner = DeepSeekRefiner(config)

# Refine code snippet
code = """
def calculate(x, y):
    return x + y
"""

result = refiner.refine_code(code, mode="document")
if result["success"]:
    print(result["refined_code"])
    print(result["explanation"])

# Refine a file
result = refiner.refine_file(
    file_path=Path("my_module.py"),
    mode="optimize",
    backup=True
)

# Batch refine
results = refiner.batch_refine(
    directory=Path("app/"),
    mode="refactor",
    exclude_patterns=["*test*", "*__init__*"]
)
print(f"Succeeded: {results['succeeded']}/{results['total_files']}")
```

## Best Practices

### When to Use Each Mode

**optimize** - Use when:
- Code has performance issues
- You need better algorithmic complexity
- Memory usage is high

**document** - Use when:
- Code lacks docstrings
- New team members need to understand code
- Preparing code for review/release

**refactor** - Use when:
- Code is difficult to maintain
- There's significant duplication
- Structure needs improvement

**security** - Use when:
- Handling user input
- Dealing with sensitive data
- Before production deployment

**test** - Use when:
- Adding tests to legacy code
- Need comprehensive test coverage
- Want to document expected behavior

**modernize** - Use when:
- Upgrading Python version
- Want to leverage new language features
- Improving code style

### Safety Tips

1. **Always use backups** when refining important code
2. **Run in dry-run mode** first for batch operations
3. **Review changes** before committing
4. **Test thoroughly** after refinement
5. **Use version control** - commit before refining
6. **Start small** - try on one file before batch processing

### Recommended Workflow

```bash
# 1. Commit current state
git add .
git commit -m "Pre-refactoring snapshot"

# 2. Test refinement on one file
python tools/deepseek_refiner.py app/example.py --mode refactor

# 3. Review and test changes
python -m pytest tests/test_example.py

# 4. If satisfied, proceed with batch
python tools/deepseek_refiner.py app/ --batch --mode refactor \
  --exclude "*test*"

# 5. Review all changes
git diff

# 6. Test entire project
python -m pytest

# 7. Commit or revert
git commit -m "Refactored app/ with DeepSeek" # or git reset --hard
```

## Troubleshooting

### API Key Not Found

**Error:** `DeepSeek API key not found`

**Solution:** Ensure DEEPSEEK_API_KEY environment variable is set:
```powershell
echo $env:DEEPSEEK_API_KEY  # Should show your key
```

### Import Error: requests

**Error:** `ModuleNotFoundError: No module named 'requests'`

**Solution:** Install requests:
```bash
pip install requests
```

### Rate Limiting

**Error:** `429 Too Many Requests`

**Solution:**
- Wait a few seconds between requests
- DeepSeek has rate limits per tier
- Consider upgrading your API plan
- Add delays in batch processing (future enhancement)

### Unexpected Output

If refinement produces unexpected results:
1. Check the explanation in the output
2. Review the original vs refined code
3. Try a different refinement mode
4. Restore from backup if needed
5. Adjust temperature in RefinementConfig (lower = more conservative)

## Configuration Options

### RefinementConfig Parameters

```python
@dataclass
class RefinementConfig:
    api_key: Optional[str] = None          # API key (or use env var)
    api_base: str = "https://api.deepseek.com/v1"  # API endpoint
    model: str = "deepseek-coder"          # Model name
    temperature: float = 0.1               # Creativity (0.0-1.0)
    max_tokens: int = 4000                 # Max response length
```

- **temperature**: Lower = more focused/deterministic, Higher = more creative
- **max_tokens**: Increase for longer files (costs more)

## Future Enhancements

Planned improvements:
- Support for other file types (JavaScript, TypeScript, etc.)
- Parallel batch processing for speed
- Custom refinement prompts
- Integration with pre-commit hooks
- Cost tracking and estimation
- Diff view before applying changes
- Rollback functionality

## Support

- **DeepSeek Docs**: https://platform.deepseek.com/docs
- **Continue Extension**: https://continue.dev/docs
- **Project Issues**: https://github.com/Obayne/AutoFireBase/issues

## Cost Estimation

DeepSeek pricing (as of 2024):
- Input: ~$0.14 per million tokens
- Output: ~$0.28 per million tokens

Typical file refinement (500 lines):
- Input: ~1500 tokens
- Output: ~1500 tokens
- Cost: ~$0.0006 per file

Batch refining 100 files: ~$0.06
