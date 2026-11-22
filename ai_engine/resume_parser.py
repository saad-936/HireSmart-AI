
import pymupdf


def extract_resume_text(pdf_path):
    """
    Extract text from a PDF resume.
    """

    try:
        document = pymupdf.open(pdf_path)

        extracted_text = ""

        for page in document:
            extracted_text += page.get_text()

        document.close()

        return extracted_text.strip()

    except Exception as error:
        print(f"Resume parsing error: {error}")
        return ""
