import os
import docx
import re

# Directory containing the downloaded documents
BASE_DIR = "dc_zoning_documents/11-A/11-A1"


def extract_title_from_doc(doc_path):
    """Extracts the title from the first few lines of a .docx file."""
    try:
        doc = docx.Document(doc_path)

        # Assuming the title is in the first paragraph, extract text
        for para in doc.paragraphs:
            text = para.text.strip()
            print(f"Extracted text from {doc_path}: {text}")  # Debug print statement
            match = re.match(r"(\d+)\s+\|\s+(.*)", text)
            if match:
                file_number, title = match.groups()
                clean_title = title.replace(" ", "_").replace("/", "-")
                return f"{file_number}_{clean_title}.docx"
    except Exception as e:
        print(f"Error reading {doc_path}: {e}")
    return None


def rename_first_document():
    """Renames only the first document in 11-A1 based on extracted title."""
    files = [f for f in os.listdir(BASE_DIR) if f.endswith(".docx")]
    if files:
        old_path = os.path.join(BASE_DIR, files[0])
        new_name = extract_title_from_doc(old_path)
        if new_name:
            new_path = os.path.join(BASE_DIR, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")
        else:
            print(f"Skipping {old_path}, unable to extract title.")
    else:
        print("No documents found in 11-A1.")


if __name__ == "__main__":
    rename_first_document()
