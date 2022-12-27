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
    product_stock = get_product_stock(moltin_token, callback).get('available')
    file_id = product_details['relationships']['files']['data'][0]['id']
    picture_href = get_image_href(moltin_token, file_id)
    product_description = f"""
        Name: {product_details.get("name")}\n
        Price: {
    product_details.get("meta").get("display_price").get("with_tax").get("formatted")
    } per kg
        Stock: {product_stock} kg on stock\n
        Description: {product_details.get("description")}"""
    keyboard = [
        [
            InlineKeyboardButton('1 кг', callback_data=f'{callback},1'),
            InlineKeyboardButton('5 кг', callback_data=f'{callback},5'),
            InlineKeyboardButton('10 кг', callback_data=f'{callback},10')
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
    else:
        product_id, product_quantity = callback.split(',')
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
            f'''{number + 1}) Name: {product['name']}
            Description: {product['description']}
            Price: ${product['unit_price']['amount']} pet kg
            {product['quantity']} kg in cart for ${product['value']['amount']}\n\n'''
            for number, product in enumerate(products_cart)
        ]
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
            text="Введите ваш email"
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
    # https://www.mygreatlearning.com/blog/regular-expression-in-python/
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        create_customer(moltin_token, email, client_id)
        update.effective_message.reply_text(
            text="Ваш заказ создан."
        )
        start(bot, update)
        return 'START'
    else:
        update.effective_message.reply_text(
            text="Вы ввели неверный email"
        )
        return 'WAITING_EMAIL'


def handle_users_reply(bot, update):
    db = get_database_connection()
    if bot:
        user_reply = bot.message.text
        chat_id = bot.message.chat_id
    elif update.message:
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
        'WAITING_EMAIL': handle_contacts
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


if __name__ == '__main__':
    env = Env()
    env.read_env()
    db = get_database_connection()
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    tgm_token = env('TGM_TOKEN')
    updater = Updater(tgm_token)
    dispatcher = updater.dispatcher
    dispatcher.chat_data['access_token'] = db.get('access_token')
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()
