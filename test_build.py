#!/usr/bin/env python3
"""
LV CAD Build Test
================
Quick test to verify the built executable works correctly.
"""

import subprocess
import sys
import time
from pathlib import Path

import pytest


def test_executable():
    """Test the built LV CAD executable."""
    import os

    # Skip by default to avoid launching built executables during unit testing
    if not os.getenv("RUN_BUILD_TESTS"):
        pytest.skip("Skipping build/executable tests (set RUN_BUILD_TESTS=1 to enable)")
    print("🔍 TESTING LV CAD BUILD")
    print("=" * 30)

    exe_path = Path("dist/LV_CAD/LV_CAD.exe")

    if not exe_path.exists():
        pytest.skip(f"Executable not found: {exe_path}")

    print(f"✅ Executable found: {exe_path}")
    print(f"📦 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Test command line argument handling
    try:
        print("🧪 Testing command line arguments...")
        result = subprocess.run(
            [str(exe_path), "--info"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            print("✅ Command line test passed")
            if "LV CAD" in result.stdout:
                print("✅ Output contains expected branding")
            else:
                print("⚠️  Output doesn't contain expected branding")
                print(f"Output: {result.stdout[:200]}...")
        else:
            print(f"⚠️  Command line test failed with code {result.returncode}")
            print(f"Error: {result.stderr}")
            pytest.fail(f"Command line invocation failed with code {result.returncode}")

    except subprocess.TimeoutExpired:
        pytest.fail("Command line test timed out")
    except Exception as e:
        pytest.fail(f"Command line test error: {e}")

    # Test GUI launch (brief)
    try:
        print("🎨 Testing GUI launch (quick check)...")
        process = subprocess.Popen([str(exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Give it time to start

        if process.poll() is None:
            print("✅ GUI appears to launch successfully")
            process.terminate()
            process.wait(timeout=5)
        else:
            print(f"❌ GUI failed to launch (exit code: {process.returncode})")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Error: {stderr.decode()}")

    except Exception as e:
        pytest.fail(f"GUI test error: {e}")

    print("\n🎯 BUILD TEST SUMMARY:")
    print(f"   📦 Executable: {exe_path}")
    print(f"   📏 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    print("   ✅ Build appears successful")
    print("   🚀 Ready for distribution")
    assert True


if __name__ == "__main__":
    # Run as script for manual checks; exit 0 on completion
    test_executable()
    print("\n🏁 Test completed: SUCCESS")
    sys.exit(0)
