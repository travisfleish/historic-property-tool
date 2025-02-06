import os
import subprocess
import docx
import re

# Directory containing the downloaded documents
BASE_DIR = "dc_zoning_documents"


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

                # Updated regex: Allows for titles with OR without leading numbers
                match = re.match(r"^(\d{1,3})?[\t\s|]*(.+)$", text)
                if match:
                    file_number = match.group(1) if match.group(1) else "NoNumber"
                    title = match.group(2).strip()
                    clean_title = title.replace(" ", "_").replace("/", "-")
                    return f"{file_number}_{clean_title}.doc"
                break  # Stop after the first valid title line
    except Exception as e:
        print(f"Error reading {doc_path}: {e}")
    return None


def rename_all_documents():
    """Renames all .doc files in BASE_DIR based on extracted titles."""
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".doc"):
                old_path = os.path.join(root, file)
                new_name = extract_title_from_doc(old_path)
                if new_name:
                    new_path = os.path.join(root, new_name)
                    os.rename(old_path, new_path)
                    print(f"Renamed: {old_path} -> {new_path}")
                else:
                    print(f"Skipping {old_path}, unable to extract title.")


if __name__ == "__main__":
    rename_all_documents()
