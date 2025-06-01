import unittest
from unittest.mock import patch, MagicMock
from app.utils.pdf_utils import PDFProxy, extract_pdf_details  # заміни на ім'я твого модуля
import fitz
import os

class TestPDFProxy(unittest.TestCase):

    @patch("proxy_module.os.path.getsize")
    @patch("proxy_module.fitz.open")
    def test_small_pdf_returns_details(self, mock_fitz_open, mock_getsize):
        # Імітуємо файл менше 95MB
        mock_getsize.return_value = 5 * 1024 * 1024  # 5MB
        mock_doc = MagicMock()
        mock_doc.page_count = 10
        mock_fitz_open.return_value = mock_doc

        proxy = PDFProxy("sample_small.pdf")
        pages, size = proxy.get_pdf_details()

        self.assertEqual(pages, 10)
        self.assertAlmostEqual(size, 5.0)

    @patch("proxy_module.os.path.getsize")
    def test_large_pdf_raises_memory_error(self, mock_getsize):
        # Імітуємо файл більше 95MB
        mock_getsize.return_value = 100 * 1024 * 1024  # 100MB
        proxy = PDFProxy("large.pdf")

        with self.assertRaises(MemoryError) as context:
            proxy.get_pdf_details()

        self.assertIn("Файл надто великий", str(context.exception))

    @patch("proxy_module.os.path.getsize")
    @patch("proxy_module.fitz.open")
    def test_lazy_loading(self, mock_fitz_open, mock_getsize):
        # PDF завантажується тільки після get_pdf_details
        mock_getsize.return_value = 1 * 1024 * 1024  # 1MB
        proxy = PDFProxy("lazy.pdf")
        self.assertIsNone(proxy._pdf_document)
        self.assertIsNone(proxy.num_pages)

        mock_doc = MagicMock()
        mock_doc.page_count = 5
        mock_fitz_open.return_value = mock_doc

        pages, size = proxy.get_pdf_details()
        self.assertEqual(pages, 5)
        self.assertIsNotNone(proxy._pdf_document)

    @patch("proxy_module.os.path.getsize")
    def test_extract_pdf_details_handles_large_files(self, mock_getsize):
        # Тест функції-обгортки
        mock_getsize.return_value = 120 * 1024 * 1024  # 120MB
        pages, size = extract_pdf_details("big.pdf")
        self.assertIsNone(pages)
        self.assertIsNone(size)
