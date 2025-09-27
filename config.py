import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Optional: Basic check
if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing API key(s). Make sure .env is set correctly.")
