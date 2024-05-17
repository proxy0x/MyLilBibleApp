# data.py

import os

def create_versions_directory():
    """
    Create a directory to store PDF versions if it doesn't exist.
    """
    try:
        os.makedirs("data/versions", exist_ok=True)
        print("Versions directory created successfully.")
    except OSError as e:
        print(f"Error creating versions directory: {e}")

def list_pdf_versions():
    """
    List all PDF versions available in the versions directory.
    
    Returns:
        list: A list of PDF filenames.
    """
    try:
        pdf_files = [file.split(".")[0] for file in os.listdir("data/versions") if file.endswith(".pdf")]
        return pdf_files
    except OSError as e:
        print(f"Error listing PDF versions: {e}")
        return []

def get_pdf_path(version_name):
    """
    Get the file path of a specific PDF version.
    
    Args:
        version_name (str): The name of the PDF version.
    
    Returns:
        str: The file path of the PDF version.
    """
    return f"data/versions/{version_name}.pdf"
