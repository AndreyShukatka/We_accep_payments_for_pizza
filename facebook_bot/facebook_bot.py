from django.conf import settings
import requests
from telegram_bot.moltin_store import checking_period_token, get_all_products, get_image_href


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


def send_menu(recipient_id):
    params = {"access_token": settings.FACEBOOK_TOKEN}
    headers = {"Content-Type": "application/json"}
    request_content = {
        'recipient': {
            'id': recipient_id,
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': menu_creation()
                }
            }
        }
    }

    response = requests.post(
        "https://graph.facebook.com/v2.6/me/messages",
        params=params, headers=headers, json=request_content

    )

    response.raise_for_status()


def menu_creation():
    moltin_token = checking_period_token()
    all_products = get_all_products(moltin_token)
    menu = []
    for number, product in enumerate(all_products):
        if number < 5:
            image_url = get_image_href(
                moltin_token,
                product.get('relationships').get('files').get('data')[0].get('id')
            )
            menu.append({
                'title': f'{product.get("name")} ({product.get("price")[0].get("amount")} руб.)',
                'image_url': image_url,
                'subtitle': product.get('description'),
                'buttons': [
                    {
                        'type': 'postback',
                        'title': 'Добавить в корзину',
                        'payload': 'DEVELOPER_DEFINED_PAYLOAD',
                    },
                ]
            })
        else:
            return menu
