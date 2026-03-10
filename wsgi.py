import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
