import os
import sys
from pathlib import Path

# Add the project root (TaskPulse/) to sys.path
project_root = Path(__file__).parent.parent  # Goes up from scripts/ to TaskPulse/
sys.path.append(str(project_root))

from api.services.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")