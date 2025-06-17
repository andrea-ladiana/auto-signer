import os
import unittest
import pdf_signer

class TestCenterPosition(unittest.TestCase):
    def test_create_watermark_center(self):
        sign_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sign.png')
        temp_path = None
        try:
            temp_path = pdf_signer.create_watermark_pdf(sign_path, position='center')
            self.assertTrue(os.path.isfile(temp_path))
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()
