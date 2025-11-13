"""
DeepSeek Refiner Demo

This script demonstrates various uses of the DeepSeek code refinement tool.
Run this to see examples of code optimization, documentation, refactoring, etc.
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.deepseek_refiner import DeepSeekRefiner, RefinementConfig


def demo_code_snippet():
    """Demo: Refine a code snippet directly"""
    print("=" * 70)
    print("DEMO 1: Refine Code Snippet")
    print("=" * 70)

    # Sample code that could be improved
    original_code = """
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result

def calculate(a, b, c):
    x = a + b
    y = x * c
    return y
"""

    print("\nOriginal Code:")
    print(original_code)

    # Initialize refiner
    try:
        refiner = DeepSeekRefiner()
    except ValueError as e:
        print(f"\n⚠️  Error: {e}")
        print("Please set DEEPSEEK_API_KEY environment variable first.")
        return False

    # Refine the code
    print("\n🔄 Refining code with 'optimize' mode...")
    result = refiner.refine_code(original_code, mode="optimize")

    if result["success"]:
        print("\n✅ Refinement successful!")
        print("\nRefined Code:")
        print(result["refined_code"])
        print("\nExplanation:")
        print(result["explanation"])
    else:
        print(f"\n❌ Refinement failed: {result['error']}")
        return False

    return True


def demo_documentation():
    """Demo: Add documentation to code"""
    print("\n" + "=" * 70)
    print("DEMO 2: Add Documentation")
    print("=" * 70)

    undocumented_code = """
class DataProcessor:
    def __init__(self, threshold):
        self.threshold = threshold
        self.processed = []

    def process(self, items):
        for item in items:
            if item > self.threshold:
                self.processed.append(item * 2)
        return self.processed

    def reset(self):
        self.processed = []
"""

    print("\nUndocumented Code:")
    print(undocumented_code)

    try:
        refiner = DeepSeekRefiner()
    except ValueError as e:
        print(f"\n⚠️  Skipping: {e}")
        return False

    print("\n🔄 Adding documentation...")
    result = refiner.refine_code(undocumented_code, mode="document")

    if result["success"]:
        print("\n✅ Documentation added!")
        print("\nDocumented Code:")
        print(result["refined_code"])
    else:
        print(f"\n❌ Failed: {result['error']}")
        return False

    return True


def demo_modernize():
    """Demo: Modernize Python code"""
    print("\n" + "=" * 70)
    print("DEMO 3: Modernize Python Code")
    print("=" * 70)

    legacy_code = """
def read_config(filename):
    config = {}
    f = open(filename, 'r')
    for line in f:
        parts = line.split('=')
        if len(parts) == 2:
            config[parts[0].strip()] = parts[1].strip()
    f.close()
    return config

def format_message(name, age, city):
    return "Name: " + name + ", Age: " + str(age) + ", City: " + city
"""

    print("\nLegacy Code:")
    print(legacy_code)

    try:
        refiner = DeepSeekRefiner()
    except ValueError as e:
        print(f"\n⚠️  Skipping: {e}")
        return False

    print("\n🔄 Modernizing code to Python 3.10+ standards...")
    result = refiner.refine_code(legacy_code, mode="modernize")

    if result["success"]:
        print("\n✅ Code modernized!")
        print("\nModernized Code:")
        print(result["refined_code"])
        print("\nExplanation:")
        print(result["explanation"])
    else:
        print(f"\n❌ Failed: {result['error']}")
        return False

    return True


def demo_custom_config():
    """Demo: Using custom configuration"""
    print("\n" + "=" * 70)
    print("DEMO 4: Custom Configuration")
    print("=" * 70)

    print("\nCustom RefinementConfig allows you to:")
    print("- Set custom temperature (creativity level)")
    print("- Adjust maximum tokens for longer responses")
    print("- Use different models")
    print("- Configure API endpoint")

    # Example custom config
    config = RefinementConfig(
        temperature=0.2,  # More creative
        max_tokens=6000,  # Longer responses
        model="deepseek-coder",
    )

    print(f"\nConfig: temperature={config.temperature}, max_tokens={config.max_tokens}")

    try:
        refiner = DeepSeekRefiner(config)
        print("✅ Custom refiner initialized successfully")
    except ValueError as e:
        print(f"⚠️  {e}")
        return False

    return True


def print_usage_tips():
    """Print helpful tips for using the refiner"""
    print("\n" + "=" * 70)
    print("USAGE TIPS")
    print("=" * 70)

    tips = [
        "1. Always backup important files before refinement",
        "2. Use --dry-run flag for batch operations to preview changes",
        "3. Start with small files to test the API connection",
        "4. Review all changes before committing to version control",
        "5. Different modes work best for different scenarios:",
        "   - optimize: Performance improvements",
        "   - document: Add comprehensive docs",
        "   - refactor: Improve code structure",
        "   - security: Identify vulnerabilities",
        "   - test: Generate unit tests",
        "   - modernize: Update to latest Python features",
        "6. Set DEEPSEEK_API_KEY environment variable before running",
        "7. Install dependencies: pip install requests",
    ]

    for tip in tips:
        print(f"  {tip}")

    print("\nQuick Start Commands:")
    print("  # Optimize a single file:")
    print("  python tools/deepseek_refiner.py app/main.py --mode optimize")
    print()
    print("  # Document entire directory (dry run):")
    print("  python tools/deepseek_refiner.py app/ --batch --mode document --dry-run")
    print()
    print("  # Generate tests for a module:")
    print(
        "  python tools/deepseek_refiner.py app/device.py --mode test --output tests/test_device.py"
    )


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("DEEPSEEK CODE REFINEMENT TOOL - DEMO")
    print("=" * 70)
    print("\nThis demo showcases various refinement capabilities.")
    print("Make sure DEEPSEEK_API_KEY environment variable is set.")

    demos = [
        ("Code Optimization", demo_code_snippet),
        ("Documentation", demo_documentation),
        ("Modernization", demo_modernize),
        ("Custom Configuration", demo_custom_config),
    ]

    results = []
    for name, demo_func in demos:
        try:
            success = demo_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Demo '{name}' crashed: {e}")
            results.append((name, False))

    # Print tips
    print_usage_tips()

    # Summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    if passed == 0:
        print("\n⚠️  All demos failed. Please check:")
        print("  1. DEEPSEEK_API_KEY environment variable is set")
        print("  2. You have internet connection")
        print("  3. DeepSeek API is accessible")

    print("\n" + "=" * 70)
    print("For full documentation, see docs/DEEPSEEK_INTEGRATION.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
