import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database ready!")
