from twilio.rest import Client

# Your Account SID from twilio.com/console
from hallxiqr.config import TWILIO_SID, TWILIO_TOKEN


class Twilio:
    def __init__(self):
        account_sid = TWILIO_SID
        auth_token = TWILIO_TOKEN
        self.client = Client(account_sid, auth_token)

    def send(self, recipient, body):
        message = self.client.messages.create(
            to=recipient,
            from_="Hall XI BoB",
            body=body
        )