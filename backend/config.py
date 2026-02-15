import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///quickcart.db")
APP_PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "1") == "1"
MODEL_PATH = os.getenv("MODEL_PATH", "models/best.pt")
print("Loaded backend.config, DATABASE_URL =", DATABASE_URL)
