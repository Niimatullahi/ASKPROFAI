from ask_gemini import ask_gemini
from pdf_reader import extract_text_from_pdf

def test_bot():
    print("🔎 Loading PDF...")
    try:
        course_file = "CSC4301.pdf"  # Change to your actual PDF name
        pdf_text = extract_text_from_pdf(course_file)
        print(f"✅ PDF loaded successfully. Content length: {len(pdf_text)} characters")
    except Exception as e:
        print(f"❌ Error loading PDF: {e}")
        return

    print("\n🤖 Asking Gemini a question...")
    try:
        question = "Explain Artificial Intelligence in simple terms as if teaching a 400-level Computer Science student at ADUSTECH."
        answer = ask_gemini(question, pdf_text)  # ✅ Pass text, not filename
        print("\n📘 Gemini’s Response:\n")
        print(answer)
    except Exception as e:
        print(f"❌ Error querying Gemini: {e}")

if __name__ == "__main__":
    test_bot()
