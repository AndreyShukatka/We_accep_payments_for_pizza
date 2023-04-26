import requests
from flask import Flask, request
from django.core.management.base import BaseCommand
from django.conf import settings
from facebook_bot.facebook_bot import send_message, send_menu


class Command(BaseCommand):
    help = 'Вебхуки для Facebook'

    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def verify():
        """
        При верификации вебхука у Facebook он отправит запрос на этот адрес. На него нужно ответить VERIFY_TOKEN.
        """
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            if not request.args.get("hub.verify_token") == settings.FACEBOOK_TOKEN:
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200
        return "Hello world", 200

    @app.route('/', methods=['POST'])
    def webhook():
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
                        send_menu(sender_id)
        return "ok", 200

    def handle(self, *args, **options):
        self.app.run(debug=True)
