import os

# Base directory = the directory where this __init__.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Subdirectories
INDIVIDUALS_PATH = os.path.join(BASE_DIR, "Individuals")
CHECK_POINTS_PATH = os.path.join(BASE_DIR, "Checkpoints")
RESULTS_PATH = os.path.join(BASE_DIR, "Results")

# Ensure the folders exist
os.makedirs(INDIVIDUALS_PATH, exist_ok=True)
os.makedirs(CHECK_POINTS_PATH, exist_ok=True)
os.makedirs(RESULTS_PATH, exist_ok=True)