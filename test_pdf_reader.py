from pdf_reader import extract_text_from_pdf

def test_pdf():
    print("🔎 Loading PDF...")
    try:
        course_file = "CSC4301.pdf"  # Change this to one of your PDF filenames in /pdfs
        text = extract_text_from_pdf(course_file)
        print(f"✅ PDF loaded successfully! Extracted {len(text)} characters.")
        print("\n📄 Preview (first 500 chars):\n")
        print(text[:500])  # Print only the first 500 chars for preview
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")

if __name__ == "__main__":
    test_pdf()
