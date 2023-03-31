from django.core.management.base import BaseCommand
from telegram_bot.tgm_bot import (
    handle_location,
    handle_users_reply,
    precheckout_callback,
    successful_payment_callback
)
from django.conf import settings
from telegram_bot.models import MoltinToken
from telegram.ext import (
    Filters,
    Updater,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    PreCheckoutQueryHandler
)

class Command(BaseCommand):
    help = 'Start telegramm bot'

    def handle(self, *args, **options):
        updater = Updater(settings.TGM_TOKEN, use_context=True)
        location_handler = MessageHandler(Filters.location, handle_location)
        dispatcher = updater.dispatcher
        dispatcher.chat_data['access_token'] = MoltinToken.objects.all().first()
        dispatcher.add_handler(
            CallbackQueryHandler(
                handle_users_reply,
                pass_job_queue=True
            )
        )
        dispatcher.add_handler(
            MessageHandler(
                Filters.text,
                handle_users_reply
            )
        )
        dispatcher.add_handler(CommandHandler('start', handle_users_reply))
        dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        dispatcher.add_handler(
            MessageHandler(
                Filters.successful_payment,
                successful_payment_callback
            )
        )
        dispatcher.add_handler(location_handler)
        updater.start_polling()
        updater.idle()
