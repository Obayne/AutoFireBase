#!/usr/bin/env python3
"""
AutoFire Device Manager CLI Tool (shim)

This script delegates to the packaged CLI in `autofire.cli.device` to avoid duplication.
"""

from autofire.cli.device import main

if __name__ == "__main__":
    main()
