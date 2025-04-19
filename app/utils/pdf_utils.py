import fitz
import os

# ==== PATTERN PROXY ==== 
# Structural 

class PDFProxy:
    MAX_FILE_SIZE_MB = 95

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self._pdf_document = None
        self.num_pages = None
        self.file_size = self._get_file_size()

    def _get_file_size(self):
        return os.path.getsize(self.pdf_path) / (1024 * 1024)

    def is_too_large(self):
        return self.file_size > self.MAX_FILE_SIZE_MB

    def _load_pdf(self):
        if self.is_too_large():
            raise MemoryError(f"Файл надто великий ({self.file_size:.2f} MB), не можна завантажити.")
        if not self._pdf_document:
            self._pdf_document = fitz.open(self.pdf_path)
            self.num_pages = self._pdf_document.page_count

    def get_pdf_details(self):
        self._load_pdf()
        return self.num_pages, self.file_size


# Використання
def extract_pdf_details(pdf_path):
    proxy = PDFProxy(pdf_path)
    try:
        return proxy.get_pdf_details()
    except MemoryError as e:
        print(e)
        return None, None  # Або поверни спеціальний об’єкт чи статус
