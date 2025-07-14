#!/usr/bin/env python3
"""Entry point script for running the Monzo app v2."""

import sys
from pathlib import Path

# Add the v2 directory to the Python path
v2_dir = Path(__file__).parent
sys.path.insert(0, str(v2_dir))

if __name__ == "__main__":
    from app import main

    main()
