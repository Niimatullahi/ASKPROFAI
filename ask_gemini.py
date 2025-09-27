import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No Gemini API key found. Please set GEMINI_API_KEY in your .env file.")

# Configure Gemini
genai.configure(api_key=API_KEY)

# Default safe model
DEFAULT_MODEL = "gemini-1.5-flash"

# Check if user set a model in .env, else fallback
MODEL_NAME = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()

# Force fallback if invalid
if MODEL_NAME not in ["gemini-1.5-flash", "gemini-1.5-pro"]:
    print(f"⚠️ Invalid or unsupported model '{MODEL_NAME}', falling back to {DEFAULT_MODEL}")
    MODEL_NAME = DEFAULT_MODEL

# Create model instance
model = genai.GenerativeModel(MODEL_NAME)

def ask_gemini(question: str, context: str = "") -> str:
    """
    Ask Gemini a question with optional context (e.g., course PDF text).
    """
    try:
        prompt = f"""
        You are AskProfAI, an academic assistant for ADUSTECH students.

        Context from course material:
        {context}

        Question:
        {question}

        Answer in a clear and simple way suitable for a 400-level Computer Science student.
        """

        response = model.generate_content(prompt)

        return response.text.strip() if response and response.text else "⚠️ No response from Gemini."

    except Exception as e:
        return f"❌ Gemini error (using {MODEL_NAME}): {e}"
