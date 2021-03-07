# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from hallxiqr.config import SENDGRID_API_KEY


class SendGrid:
    from_email = ('admin@hallxi.com', 'Hall XI BoB')
    api_key = SENDGRID_API_KEY

    def __init__(self):
        self.sg = SendGridAPIClient(self.api_key)

    def send(self, recipient, subject, message):

        message = Mail(
            from_email=self.from_email,
            to_emails=recipient,
            subject=subject,
            html_content=message)
        try:
            self.sg.send(message)
        except Exception as e:
            print(repr(e))
