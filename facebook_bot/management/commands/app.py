import os

import requests
from flask import Flask, request
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Вебхуки для Facebook'

    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def verify(self):
        """
        При верификации вебхука у Facebook он отправит запрос на этот адрес. На него нужно ответить VERIFY_TOKEN.
        """
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200

        return "Hello world", 200

    @app.route('/', methods=['POST'])
    def webhook(self):
        """
        Основной вебхук, на который будут приходить сообщения от Facebook.
        """
        data = request.get_json()
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]
                        recipient_id = messaging_event["recipient"]["id"]
                        message_text = messaging_event["message"]["text"]
                        self.send_message(sender_id, message_text)
        return "ok", 200

    def send_message(recipient_id, message_text):
        params = {"access_token": settings.FACEBOOK_TOKEN}
        headers = {"Content-Type": "application/json"}
        request_content = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        }
        response = requests.post(
            "https://graph.facebook.com/v2.6/me/messages",
            params=params, headers=headers, json=request_content
        )
        response.raise_for_status()

    def handle(self, *args, **options):
        app = Flask(__name__)
        app.run(debug=True)
