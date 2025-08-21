"""
Zelda 2D - entry point
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.game import main

if __name__ == "__main__":
    main()
