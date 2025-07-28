"""
Main entry point for the enhanced Flappy Birds game.
This file serves as the primary executable for the game.
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.game import main

if __name__ == "__main__":
    main()
