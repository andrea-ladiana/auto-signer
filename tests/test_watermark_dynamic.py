import unittest
import os
from reportlab.lib.pagesizes import A4
from pdf_signer import create_watermark_pdf, calculate_watermark_size_points
import PyPDF2

class TestWatermarkPageSize(unittest.TestCase):
    def test_position_on_a4(self):
        scale = 0.2
        page_size = A4
        pdf_path = create_watermark_pdf(
            'sign.png', scale_factor=scale, position='bottom-right', page_size=page_size
        )
        try:
            self.assertTrue(os.path.exists(pdf_path))
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                page = reader.pages[0]
                self.assertAlmostEqual(float(page.mediabox.width), page_size[0], places=2)
                self.assertAlmostEqual(float(page.mediabox.height), page_size[1], places=2)
                content = page.get_contents().get_data().decode('latin1')
                lines = [l.strip() for l in content.splitlines()]
                idx = lines.index('q')
                matrix_line = lines[idx + 1]
                numbers = [float(n) for n in matrix_line.split()[:6]]
                width = numbers[0]
                height = numbers[3]
                x = numbers[4]
                y = numbers[5]
                expected_w, expected_h, _, _ = calculate_watermark_size_points('sign.png', scale)
                margin = 20
                expected_x = page_size[0] - expected_w - margin
                expected_y = margin
                self.assertAlmostEqual(width, expected_w, places=2)
                self.assertAlmostEqual(height, expected_h, places=2)
                self.assertAlmostEqual(x, expected_x, places=2)
                self.assertAlmostEqual(y, expected_y, places=2)
        finally:
            os.unlink(pdf_path)

if __name__ == '__main__':
    unittest.main()
