import requests
from environs import Env
import argparse
from datetime import datetime, timedelta


def get_args():
    parser = argparse.ArgumentParser(
        description='Программа для работы с API магазина moltin'
    )
    parser.add_argument(
        '--create_product',
        help='Добавить продукт в магазин, укажите: product_name, sku, description, amount, по умолчанию False',
        action='store_true'
    )
    parser.add_argument(
        '--create_inventory_store',
        help='Заполнить количество на складе, нужен product_id и quantity',
        action='store_true'
    )
    parser.add_argument(
        '--del_product',
        help='Удалить продукт из магазина, нужен product_id',
        action='store_true'
    )
    parser.add_argument(
        '--create_file',
        help='Загрузить файл на сайт через url, нужен file_url',
        action='store_true'
    )
    parser.add_argument(
        '--create_file_relationship',
        help='Привязать фотографию к товару',
        action='store_true'
    )
    parser.add_argument(
        '--file_url',
        help='Ссылка на файл'
    )
    parser.add_argument(
        '--image_id',
        help='Ввести id фотографии товара'
    )
    parser.add_argument(
        '--quantity',
        help='Количество товара',
        type=int
    )
    parser.add_argument(
        '--product_name',
        help='Наименование продукта',
        nargs='+'
    )
    parser.add_argument(
        '--get_all_products',
        help='Посмотреть все добавленные в магазин товары',
        action="store_true"
    )
    parser.add_argument(
        '--sku',
        help='SKU продукта'
    )
    parser.add_argument(
        '--description',
        help='Описание продукта',
        nargs='+'
    )
    parser.add_argument(
        '--manage_stock',
        help='Менеджмент продукта, по умолчанию True',
        default=True
    )
    parser.add_argument(
        '--amount',
        help='Цена продукта'
    )
    parser.add_argument(
        '--product_status',
        help='Статус продукта, по умолчанию live',
        default='live'
    )
    parser.add_argument(
        '--product_id',
        help='id продукта'
    )
    args = parser.parse_args()
    return args


def get_moltin_token(moltin_client_id, moltin_client_secret, db=None):
    url = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': moltin_client_id,
        'client_secret': moltin_client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    if db:
        now_time = datetime.now()
        token_expiration = int(response.json().get('expires_in'))
        seconds = int(60)
        minutes_token_expiration = token_expiration / seconds
        token_end_time = now_time + timedelta(minutes=minutes_token_expiration)
        db.set('access_token', response.json().get('access_token'))
        db.set('token_creation_time', str(now_time))
        db.set('token_end_time', str(token_end_time))
    return response.json().get('access_token')


def checking_period_token(moltin_client_id, moltin_client_secret, db):
    date_formatter = '%Y-%m-%d %H:%M:%S.%f'
    if db.get('token_creation_time'):
        now_time = datetime.now()
        token_creation_time = datetime.strptime(db.get('token_creation_time').decode(), date_formatter)
        token_end_time = datetime.strptime(db.get('token_end_time').decode(), date_formatter)
        if token_creation_time <= now_time <= token_end_time:
            moltin_token = db.get('access_token').decode('utf-8')
            return moltin_token
        else:
            moltin_token = get_moltin_token(moltin_client_id, moltin_client_secret, db)
            return moltin_token
    else:
        moltin_token = get_moltin_token(moltin_client_id, moltin_client_secret, db)
        return moltin_token


def get_all_products(moltin_token):
    url = 'https://api.moltin.com/v2/products'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('data')


def get_product(moltin_token, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}'
    headers = {
        'Authorization': f'Bearer {moltin_token}',
    }

    product = requests.get(url=url, headers=headers)
    product.raise_for_status()
    return product.json().get('data')


def get_cart(moltin_token, client_id):
    url = f'https://api.moltin.com/v2/carts/{client_id}'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get(
        'data'
    ).get(
        'meta'
    ).get(
        'display_price'
    ).get(
        'with_tax'
    ).get(
        'formatted'
    )


def get_cart_items(moltin_token, client_id):
    url = f'https://api.moltin.com/v2/carts/{client_id}/items'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('data')


def add_product_cart(moltin_token, client_id, product_id, product_quantity):
    url = f'https://api.moltin.com/v2/carts/{client_id}/items'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    json_data = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": int(product_quantity)
        }
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()


def del_product_cart(moltin_token, priduct_id, client_id):
    url = f'https://api.moltin.com/v2/carts/{client_id}/items/{priduct_id}'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def create_product_store(
        moltin_token,
        product_name,
        product_sku,
        product_description,
        manage_stock,
        product_amount,
        product_status
):
    url = 'https://api.moltin.com/v2/products'
    headers = {
        'Authorization': f'Bearer {moltin_token}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': {
            'type': 'product',
            'name': ''.join(product_name),
            'slug': product_sku,
            'sku': product_sku,
            'description': ''.join(product_description),
            'manage_stock': manage_stock,
            'price': [
                {
                    'amount': product_amount,
                    'currency': 'RUB',
                    'includes_tax': True,
                },
            ],
            'status': product_status,
            'commodity_type': 'physical',
        },
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json().get('data')


def del_product_store(moltin_token, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}'
    headers = {
        'Authorization': f'Bearer {moltin_token}',
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def create_file_relationship(moltin_token, image_id, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}/relationships/files'
    headers = {
        'Authorization': f'Bearer {moltin_token}',
        'Content-Type': 'application/json'
    }
    json_data = {
        'data': [
            {
                'type': 'file',
                'id': image_id
            }
        ]
    }
    response = requests.post(
        url,
        headers=headers,
        json=json_data
    )
    response.raise_for_status()
    return response.json().get('data')


def create_inventory_store(moltin_token, quantity, product_id):
    url = f'https://api.moltin.com/v2/inventories/{product_id}/transactions'
    headers = {
        'Authorization': f'Bearer {moltin_token}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': {
            'type': 'stock-transaction',
            'action': 'increment',
            'quantity': {quantity},
        },
    }

    response = requests.post(
        url,
        headers=headers,
        json=json_data,
    )
    response.raise_for_status()


def get_product_stock(moltin_token, product_id):
    url = f'https://api.moltin.com/v2/inventories/{product_id}'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('data')


def get_image_href(moltin_token, file_id):
    url = f'https://api.moltin.com/v2/files/{file_id}'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('data').get('link').get('href')


def create_customer(moltin_token, email, client_id):
    url = 'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': f'Bearer {moltin_token}',
        'Content-Type': 'application/json'
    }
    json_data = {
        'data': {
            'type': 'customer',
            'name': str(client_id),
            'email': email,
            'password': ''
        },
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()


def create_file(moltin_token, file_url):
    url = 'https://api.moltin.com/v2/files'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    files = {
        'file_location': (None, file_url),
    }
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json().get('data')


def create_flow(moltin_token, flow_name, flow_description, flow_status=True):
    url = 'https://api.moltin.com/v2/flows'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    json_data = {
        'data': {
            'type': 'flow',
            'name': flow_name,
            'slug': flow_name,
            'description': flow_description,
            'enabled': flow_status
        },
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    print(response.json())
    return response.json()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_token = get_moltin_token(
        moltin_client_id,
        moltin_client_secret
    )
    args = get_args()
    if args.create_product:
        product_name = args.product_name
        sku = args.sku
        description = args.description
        manage_stock = args.manage_stock
        amount = args.amount
        product_status = args.product_status
        create_product_store(
            moltin_token,
            product_name,
            sku,
            description,
            manage_stock,
            amount,
            product_status
        )
    elif args.del_product:
        product_id = args.product_id
        del_product_store(moltin_token, product_id)
    elif args.get_all_products:
        print(get_all_products(moltin_token))
    elif args.create_inventory_store:
        quantity = args.quantity
        product_id = args.product_id
        create_inventory_store(moltin_token, quantity, product_id)
    elif args.create_file_relationship:
        product_id = args.product_id
        image_id = args.image_id
        create_file_relationship(moltin_token, image_id, product_id)
    elif args.create_file:
        file_url = args.file_url
        create_file(moltin_token, file_url)
