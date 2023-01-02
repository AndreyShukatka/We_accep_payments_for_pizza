import redis
import re
from environs import Env
from moltin_store import (
    get_all_products,
    get_product,
    get_product_stock,
    get_image_href,
    add_product_cart,
    get_cart,
    get_cart_items,
    del_product_cart,
    create_customer,
    checking_period_token
)
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Filters,
    Updater,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler
)

_database = None


def start(bot, update):
    keyboard = []
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret, db)
    all_products = get_all_products(moltin_token)
    for product in all_products:
        keyboard.append([InlineKeyboardButton(
            product.get('name'),
            callback_data=product.get('id')
        )])
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(
        text='Выберите пожалуйста товар:',
        reply_markup=reply_markup
    )
    update.effective_message.delete()
    return 'HANDLE_MENU'


def handle_menu(bot, update):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret, db)
    query = update.callback_query
    callback = query.data
    if callback == 'cart':
        handle_cart(bot, update)
        return 'HANDLE_CART'
    product_details = get_product(moltin_token, callback)
    file_id = product_details['relationships']['files']['data'][0]['id']
    picture_href = get_image_href(moltin_token, file_id)
    product_description = f'{product_details.get("name")} \nСтоимость: {product_details.get("price")[0].get("amount")} рублей \n\n{product_details.get("description")} '
    keyboard = [
        [
            InlineKeyboardButton('Положить в корзину', callback_data=f'{callback},1'),
        ],
        [InlineKeyboardButton('Корзина', callback_data='cart')],
        [InlineKeyboardButton('В меню', callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_photo(
        chat_id=query.message.chat_id,
        photo=picture_href,
        caption=product_description,
        reply_markup=reply_markup,
        reply_to_message_id=query.message.message_id
    )
    update.effective_message.delete()
    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret, db)
    query = update.callback_query
    callback = query.data
    client_id = query['message']['chat']['id']
    total_price = get_cart(moltin_token, client_id)
    if callback == 'start':
        start(bot, update)
        return 'HANDLE_MENU'
    elif callback == 'cart':
        products_cart = get_cart_items(moltin_token, client_id)
        keyboard = [
            [
                InlineKeyboardButton(
                    f"Удалить {product['name']}", callback_data=product["id"]
                )
            ]
            for product in products_cart
        ]
        if products_cart:
            keyboard.append(
                [InlineKeyboardButton('Оплата', callback_data='pay')]
            )
        keyboard.append(
            [InlineKeyboardButton('В меню', callback_data='start')]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        cart_description = [
            f'''{product['name']}
            {product['description']}
            {product['quantity']} пицц в корзине на сумму {product['value']['amount']} рублей\n\n'''
            for product in products_cart]
        cart_description.append(f'Total: {total_price}')
        update.effective_message.reply_text(
            text="".join(cart_description),
            reply_markup=reply_markup
        )
        update.effective_message.delete()
        return "HANDLE_CART"
    else:
        product_id, product_quantity = callback.split(',')
        print(product_quantity, product_id)
        add_product_cart(moltin_token, client_id, product_id, product_quantity)

        return "HANDLE_DESCRIPTION"


def handle_cart(bot, update):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret, db)
    query = update.callback_query
    callback = query.data
    client_id = query['message']['chat']['id']
    if callback == 'cart':
        products_cart = get_cart_items(moltin_token, client_id)
        total_price = get_cart(moltin_token, client_id)
        keyboard = [
            [
                InlineKeyboardButton(
                    f"Удалить {product['name']}", callback_data=product["id"]
                )
            ]
            for product in products_cart
        ]
        if products_cart:
            keyboard.append(
                [InlineKeyboardButton('Оплата', callback_data='pay')]
            )
        keyboard.append(
            [InlineKeyboardButton('В меню', callback_data='start')]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        cart_description = [
            f'''{product['name']}
            {product['description']}
            {product['quantity']} пицц в корзине на сумму {product['value']['amount']} рублей\n\n'''
            for product in products_cart]
        cart_description.append(f'Total: {total_price}')
        update.effective_message.reply_text(
            text=''.join(cart_description),
            reply_markup=reply_markup
        )
        update.effective_message.delete()
        return "HANDLE_CART"
    elif callback == 'start':
        start(bot, update)
        return 'HANDLE_MENU'
    elif callback == 'pay':
        update.effective_message.reply_text(
            text="Хорошо, пришлите нам ваш адрес текстом или геолокацию"
        )
        return 'WAITING_EMAIL'
    else:
        del_product_cart(moltin_token, callback, client_id)
        total_price = get_cart(moltin_token, client_id)
        products_cart = get_cart_items(moltin_token, client_id)
        keyboard = [
            [
                InlineKeyboardButton(
                    f"Удалить {product['name']}", callback_data=product["id"]
                )
            ]
            for product in products_cart
        ]
        keyboard.append(
            [InlineKeyboardButton('В меню', callback_data='start')]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        cart_description = [
            f'''{number + 1}) Name: {product['name']}
            Description: {product['description']}
            Price: ${product['unit_price']['amount']} pet kg
            {product['quantity']} kg in cart for ${product['value']['amount']}\n\n'''
            for number, product in enumerate(products_cart)]
        cart_description.append(f'Total: {total_price}')
        update.effective_message.reply_text(
            text="".join(cart_description),
            reply_markup=reply_markup
        )
        update.effective_message.delete()
        return "HANDLE_CART"


def handle_contacts(bot, update):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret, db)
    email = update.message.text
    client_id = update.message.chat_id
    update.effective_message.reply_text(
        text="Ваш заказ создан."
    )
    start(bot, update)
    return 'START'



def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        "START": start,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_MENU': handle_menu,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': get_location,
        'HANDLE_WAITING': 'handle_waiting'
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = env('REDIS_PASSWORD')
        database_host = env('REDIS_HOST')
        database_port = env('REDIS_PORT')
        _database = redis.Redis(
            host=database_host,
            port=database_port,
            password=database_password
        )
    return _database


def get_location(bot, update):
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    if message.location:
        coordinates = (message.location.latitude, message.location.longitude)
    else:
        address = message.text
        coordinates = fetch_coordinates(yandex_api_key, address)
    update.effective_message.reply_text(
        text=coordinates
    )
    return


def fetch_coordinates(yandex_api_key, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": yandex_api_key,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


if __name__ == '__main__':
    env = Env()
    env.read_env()
    db = get_database_connection()
    yandex_api_key = env('YANDEX_API_KEY')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    tgm_token = env('TGM_TOKEN')
    updater = Updater(tgm_token)
    location_handler = MessageHandler(Filters.location, get_location)
    dispatcher = updater.dispatcher
    dispatcher.chat_data['access_token'] = db.get('access_token')
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(location_handler)
    updater.start_polling()
    updater.idle()
