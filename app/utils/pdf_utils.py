import fitz
import os

def extract_pdf_details(pdf_path):
    document = fitz.open(pdf_path)
    num_pages = document.page_count
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)
    return num_pages, file_size