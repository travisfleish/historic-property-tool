import os
import subprocess
import docx
import re

# Directory containing the downloaded documents
BASE_DIR = "dc_zoning_documents/11-A/11-A1"


def convert_doc_to_docx(doc_path):
    """Converts a .doc file to .docx using LibreOffice (Mac/Linux compatible)."""
    docx_path = doc_path + "x"
    try:
        subprocess.run(
            ["/Applications/LibreOffice.app/Contents/MacOS/soffice", "--headless", "--convert-to", "docx", doc_path,
             "--outdir", os.path.dirname(doc_path)], check=True)
        return docx_path if os.path.exists(docx_path) else None
    except Exception as e:
        print(f"Error converting {doc_path} to .docx: {e}")
        return None


def extract_title_from_doc(doc_path):
    """Extracts the title from the first few lines of a .doc file."""
    docx_path = convert_doc_to_docx(doc_path)
    if not docx_path:
        return None

    try:
        doc = docx.Document(docx_path)
        os.remove(docx_path)  # Clean up converted file

        # Extract the first meaningful paragraph
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                print(f"Extracted potential title from {doc_path}: {text}")  # Debug print statement

                # Improved regex to handle varying spaces/tabs
                match = re.match(r"^(\d{3,})[\t\s|]+(.+)$", text)
                if match:
                    file_number, title = match.groups()
                    clean_title = title.replace(" ", "_").replace("/", "-")
                    return f"{file_number}_{clean_title}.doc"
                break  # Stop after the first valid title line
    except Exception as e:
        print(f"Error reading {doc_path}: {e}")
    return None


def rename_first_document():
    """Renames only the first document in 11-A1 based on extracted title."""
    files = [f for f in os.listdir(BASE_DIR) if f.endswith(".doc")]
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