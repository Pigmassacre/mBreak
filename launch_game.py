#!/usr/bin/env python
"""
mBreak Game Launcher

This script launches the mBreak game by running the mBreak.py file
from the python/ directory regardless of where this launcher is run from.
"""

import os
import sys
import subprocess

# Get the directory containing this script
base_dir = os.path.dirname(os.path.abspath(__file__))
game_script = os.path.join(base_dir, "python", "mBreak.py")

# Change to the python directory before launching
os.chdir(os.path.join(base_dir, "python"))

# For Windows, we use the python executable to run the script
if sys.platform.startswith('win'):
    python_executable = sys.executable
    subprocess.run([python_executable, game_script])
else:
    # For Linux/Mac, we can use direct execution if the script has execute permissions
    subprocess.run([game_script])

print("Game has exited.") 