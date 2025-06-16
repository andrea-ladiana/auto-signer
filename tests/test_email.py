import ssl
import unittest
from unittest.mock import patch, MagicMock, mock_open

from pdf_signer import send_email_with_pdf


class TestSendEmailWithPDF(unittest.TestCase):
    def setUp(self):
        self.pdf_path = 'dummy.pdf'
        self.recipients = ['user@example.com']
        self.ssl_ctx = ssl.create_default_context()

    @patch('pdf_signer.smtplib.SMTP')
    @patch('pdf_signer.smtplib.SMTP_SSL')
    def test_use_ssl_when_tls_disabled_and_port_465(self, mock_ssl, mock_smtp):
        email_cfg = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 465,
            'username': 'u',
            'password': 'p',
            'use_tls': False,
        }
        server = MagicMock()
        mock_ssl.return_value = server
        m = mock_open()
        m.return_value.read.return_value = b'data'
        with patch('builtins.open', m), patch('os.path.exists', return_value=True):
            send_email_with_pdf(self.pdf_path, email_cfg, self.recipients, ssl_context=self.ssl_ctx)
        mock_ssl.assert_called_once_with('smtp.example.com', 465, context=self.ssl_ctx)
        mock_smtp.assert_not_called()
        server.starttls.assert_not_called()

    @patch('pdf_signer.smtplib.SMTP')
    @patch('pdf_signer.smtplib.SMTP_SSL')
    def test_use_starttls_when_enabled(self, mock_ssl, mock_smtp):
        email_cfg = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'username': 'u',
            'password': 'p',
            'use_tls': True,
        }
        server = MagicMock()
        mock_smtp.return_value = server
        m = mock_open()
        m.return_value.read.return_value = b'data'
        with patch('builtins.open', m), patch('os.path.exists', return_value=True):
            send_email_with_pdf(self.pdf_path, email_cfg, self.recipients, ssl_context=self.ssl_ctx)
        mock_smtp.assert_called_once_with('smtp.example.com', 587)
        mock_ssl.assert_not_called()
        server.starttls.assert_called_once_with(context=self.ssl_ctx)


if __name__ == '__main__':
    unittest.main()
