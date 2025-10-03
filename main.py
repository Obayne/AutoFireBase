#!/usr/bin/env python3
"""
AutoFire - Fire Alarm CAD Application
Clean entry point following modular architecture.
"""

import os
import sys

# Add current directory to path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))

from frontend.app import main

if __name__ == "__main__":
    sys.exit(main())
