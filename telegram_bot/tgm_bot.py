from geopy import distance
from telegram import (LabeledPrice, ShippingOption)
import textwrap
from .models import TelegramUser
from environs import Env
from .moltin_store import (
    get_all_products,
    get_product,
    get_product_stock,
    get_image_href,
    add_product_cart,
    get_cart,
    get_cart_items,
    del_product_cart,
    get_all_entries,
    checking_period_token,
    create_entry,
    get_enteries
)
import requests

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import (
    Filters,
    Updater,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler
)

env = Env()
env.read_env()
moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
moltin_client_id = env('MOLTIN_CLIENT_ID')
yandex_api_key = env('YANDEX_API_KEY')


def start(update, context):
    keyboard = []
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret)
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


def handle_menu(update, context):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret)
    query = update.callback_query
    callback = query.data
    if callback == 'cart':
        handle_cart(update, context)
        return 'HANDLE_CART'
    if callback == 'start':
        start(update, context)
        return 'HANDLE_MENU'
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
    context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=picture_href,
        caption=product_description,
        reply_markup=reply_markup,
        reply_to_message_id=query.message.message_id
    )
    update.effective_message.delete()
    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret)
    query = update.callback_query
    callback = query.data
    client_id = query['message']['chat']['id']
    total_price = get_cart(moltin_token, client_id)
    if callback == 'start':
        start(update, context)
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
            textwrap.dedent(f'''
            {product['name']}
            {product['description']}
            {product['quantity']} пицц в корзине на сумму {product['value']['amount']} рублей\n
            ''')
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
        add_product_cart(moltin_token, client_id, product_id, product_quantity)

        return "HANDLE_DESCRIPTION"


def handle_cart(update, context):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret)
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
        start(update, context)
        return 'HANDLE_MENU'
    elif callback == 'pay':
        update.effective_message.reply_text(
            text="Хорошо, пришлите нам ваш адрес текстом или геолокацию"
        )
        update.effective_message.delete()
        return 'WAITING_LOCATION'
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
            f'''
{number + 1}) Name: {product['name']}
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


def handle_contacts(update, context):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret)
    email = update.message.text
    client_id = update.message.chat_id
    update.effective_message.reply_text(
        text="Ваш заказ создан."
    )
    start(update, context)
    return 'START'


def handle_users_reply(update, context):
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
        user_state = TelegramUser.objects.get(chat_id=chat_id).next_state
    states_functions = {
        "START": start,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_MENU': handle_menu,
        'HANDLE_CART': handle_cart,
        'WAITING_LOCATION': handle_location,
        'HANDLE_PAYMENT': handle_payment,
        'HANDLE_DELIVERY': handle_delivery,
        'HANDLE_PICKUP': handle_pickup
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        if TelegramUser.objects.filter(chat_id=chat_id):
            user = TelegramUser.objects.get(chat_id=chat_id)
            user.next_state = next_state
            user.save()
        else:
            TelegramUser.objects.create(
                chat_id=chat_id,
                next_state=next_state
            )
    except Exception as err:
        print(err)


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
    return lat, lon


def handle_location(update, context):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret)
    flow_name = 'Pizzeria'
    keyboard = [
        [InlineKeyboardButton("Самовывоз", callback_data='pickup')],
        [InlineKeyboardButton("Доставка", callback_data='delivery')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = update.message
    if update.callback_query:
        if update.callback_query.data == 'delivery':
            handle_payment(update, context)
            handle_delivery(update, context)
            return 'HANDLE_DELIVERY'
        else:
            handle_pickup(update, context)
            return 'HANDLE_MENU'
    if message.location:
        user_coordinates = (message.location.latitude, message.location.longitude)
    else:
        address = message.text
        user_coordinates = fetch_coordinates(yandex_api_key, address)
    min_distance = get_min_distance(moltin_token, flow_name, user_coordinates)
    user = TelegramUser.objects.get(chat_id=message.chat_id)
    user.address_pizzeria = min_distance['address']
    user.save()
    if min_distance['distance'] < 0.5:
        update.effective_message.reply_text(
            text=f'Может, заберете пиццу из нашей пиццерии неподалёку? Она всего в {int(min_distance["distance"] * 100)} метрах от вас! '
                 f'Вот её адрес: {min_distance["address"]}. '
                 f'А можем и бесплатно доставить.',
            reply_markup=reply_markup
        )
    elif 0.5 < min_distance['distance'] < 5:
        update.effective_message.reply_text(
            text=f'Похоже, придется ехать до вас на самокате. Доставка будет стоить 100 рублей. Доставляем или самовывоз?',
            reply_markup=reply_markup
        )
    elif 5 < min_distance['distance'] < 20:
        update.effective_message.reply_text(
            text=f'Похоже, придется ехать до вас на автомобиле. Доставка будет стоить 300 рублей. Доставляем или самовывоз?',
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [InlineKeyboardButton("Самовывоз", callback_data='Самовывоз')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.effective_message.reply_text(
            text=f'Простите, но так далеко мы пиццу не доставим. Ближайшая пиццерия аж в {int(min_distance["distance"])} километрах от вас!',
            reply_markup=reply_markup
        )
    user_address = message.text
    user_lon = user_coordinates[0]
    user_lat = user_coordinates[1]
    fill_fields = {
        'type': 'entry',
        'telegramm_user_id': message.chat_id,
        'user_address_delivery': user_address,
        'Longitude': user_lon,
        'Latitude': user_lat
    }
    flow_name = 'customer_Address'
    create_entry(moltin_token, flow_name, fill_fields, )
    update.effective_message.delete()
    return 'HANDLE_DELIVERY'

def handle_delivery(update, context):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret)
    client_id = update.callback_query.message.chat_id
    flow_name_address = 'customer_Address'
    flow_name_pizzeria = 'Pizzeria'
    deliveri_address = [
        x for x in get_all_entries(moltin_token, flow_name=flow_name_address)
        if x['telegramm_user_id'] == str(client_id)
    ][0]
    user_coordinates = [deliveri_address.get('Longitude'), deliveri_address.get('Latitude')]
    pizzeria = get_min_distance(moltin_token, flow_name_pizzeria, user_coordinates)
    deliveriman = [
        x for x in get_all_entries(moltin_token, flow_name=flow_name_pizzeria)
        if x['Address'] == pizzeria.get('address')
    ][0].get('Deliveryman')
    products_cart = get_cart_items(moltin_token, client_id)
    total_price = get_cart(moltin_token, client_id)
    cart_description = [
        textwrap.dedent(f'''
        {product['name']}
        {product['description']}
        {product['quantity']} пицц в корзине на сумму {product['value']['amount']} рублей\n
        ''')
        for product in products_cart]
    cart_description.append(textwrap.dedent(f'К оплате {total_price} рублей'))
    context.bot.send_message(
        chat_id=deliveriman,
        text=''.join(cart_description),
    )
    context.bot.send_location(
        chat_id=deliveriman,
        latitude=deliveri_address.get('Longitude'),
        longitude=deliveri_address.get('Latitude')
    )
    remind_via = 3600
    context.job_queue.run_once(send_delivery_notification, remind_via, context=client_id)
    return 'HANDLE_PAYMENT'

def handle_pickup(update, context):
    min_distance = TelegramUser.objects.get(chat_id=update.callback_query.message.chat_id).address_pizzeria
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(
        text=f'Ближайшая пиццерия к Вам: \n {min_distance}',
        reply_markup=reply_markup
    )
    return 'HANDLE_PICKUP'


def get_min_distance(moltin_token, flow_name, user_coordinates):
    all_moltin_pizzerias = get_all_entries(moltin_token, flow_name)
    distance_all_pizzerias = []
    for pizzeria in all_moltin_pizzerias:
        pizzeria_lon = pizzeria['Longitude']
        pizzeria_lat = pizzeria['Latitude']
        pizzeria_coor = [pizzeria_lat, pizzeria_lon]
        user_distance = distance.distance(user_coordinates, pizzeria_coor)
        distance_all_pizzerias.append({
            'address': pizzeria.get('Address'),
            'distance': user_distance.km
        })

    def get_address_distance(address):
        return address['distance']

    min_distance = min(distance_all_pizzerias, key=get_address_distance)
    return min_distance


def send_delivery_notification(context):
    message = textwrap.dedent(f'''
    Приятного аппетита! *место для рекламы*\n
    *сообщение что делать если пицца не пришла*
    ''')
    job = context.job
    context.bot.send_message(job.context, text=message)


def handle_payment(update, context):
    moltin_token = checking_period_token(moltin_client_id, moltin_client_secret)
    client_id = update.callback_query.message.chat_id
    products_cart = get_cart_items(moltin_token, client_id)
    total_price = get_cart(moltin_token, client_id)
    title = "Оплата заказа"
    cart_description = [
        'Test payment'
        ]
    # select a payload just for you to recognize its the donation from your bot
    payload = env('PAYLOAD')
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    provider_token = env('BANK_TOKEN')
    start_parameter = "test-payment"
    currency = "RUB"
    # price in dollars
    # price * 100 so as to include 2 d.p.
    prices = [LabeledPrice(label=product['name'], amount=product['value']['amount']*10)
              for product in products_cart]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.sendInvoice(client_id, title, cart_description, payload,
                    provider_token, start_parameter, currency, prices)


def precheckout_callback(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != env('PAYLOAD'):
        query.answer(ok=False, error_message="Что-то пошло не так...")
    else:
        query.answer(ok=True)


def successful_payment_callback(update, context):
    keyboard = [[InlineKeyboardButton(f'Продолжить', callback_data='card_confirm')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Спасибо за Вашу оплату!", reply_markup=reply_markup)
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

