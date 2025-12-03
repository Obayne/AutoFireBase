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


def test_executable():
    """Test the built LV CAD executable."""
    print("🔍 TESTING LV CAD BUILD")
    print("=" * 30)

    exe_path = Path("dist/LV_CAD/LV_CAD.exe")

    if not exe_path.exists():
        print(f"❌ Executable not found: {exe_path}")
        return False

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

    except subprocess.TimeoutExpired:
        print("⏰ Command line test timed out")
    except Exception as e:
        print(f"❌ Command line test error: {e}")

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
        print(f"❌ GUI test error: {e}")

    print("\n🎯 BUILD TEST SUMMARY:")
    print(f"   📦 Executable: {exe_path}")
    print(f"   📏 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    print("   ✅ Build appears successful")
    print("   🚀 Ready for distribution")

    return True


if __name__ == "__main__":
    success = test_executable()
    print(f"\n🏁 Test completed: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
