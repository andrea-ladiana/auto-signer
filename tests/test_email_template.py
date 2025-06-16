import os
import sys
import smtplib

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pdf_signer import send_email_with_pdf

class DummySMTP:
    def __init__(self, server, port):
        self.sent_message = None
    def starttls(self):
        pass
    def login(self, user, pwd):
        pass
    def send_message(self, msg):
        self.sent_message = msg
    def quit(self):
        pass


def test_placeholder_substitution(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_text("dummy")
    template = tmp_path / "tmpl.txt"
    template.write_text("Hello {filename} - {timestamp}")

    smtp_instance = DummySMTP("", 0)
    monkeypatch.setattr(smtplib, "SMTP", lambda *args, **kwargs: smtp_instance)

    config = {
        "server": "localhost",
        "port": 25,
        "username": "",
        "password": "",
        "use_tls": False,
    }

    send_email_with_pdf(str(pdf), config, ["dest@example.com"], template_path=str(template))

    assert smtp_instance.sent_message is not None
    body_part = smtp_instance.sent_message.get_payload()[0]
    body = body_part.get_payload(decode=True).decode("utf-8")
    assert "doc.pdf" in body
    assert "{filename}" not in body
