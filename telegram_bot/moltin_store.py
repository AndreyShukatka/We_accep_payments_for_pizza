import requests
from datetime import datetime, timedelta
from .models import MoltinToken


def get_moltin_token(moltin_client_id, moltin_client_secret):
    url = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': moltin_client_id,
        'client_secret': moltin_client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    token_params = response.json()
    date_formatter = '%Y-%m-%d %H:%M:%S'
    now_time = datetime.now()
    token_expiration = int(token_params.get('expires_in'))
    seconds_in_minute = int(60)
    minutes_token_expiration = token_expiration / seconds_in_minute
    token_end_time = now_time + timedelta(minutes=minutes_token_expiration)
    MoltinToken(
        access_token=token_params.get('access_token'),
        token_creation_time=now_time.strftime(date_formatter),
        token_end_time=token_end_time.strftime(date_formatter),
        active_token=True
    ).save()
    return token_params.get('access_token')


def checking_period_token(moltin_client_id, moltin_client_secret):
    date_formatter = '%Y-%m-%d %H:%M:%S'
    if MoltinToken.objects.filter(active_token=True):
        moltin_token = MoltinToken.objects.get(active_token=True)
        now_time = datetime.now()
        token_creation_time = datetime.strptime(
            str(moltin_token.token_creation_time),
            date_formatter
        )
        token_end_time = datetime.strptime(
            str(moltin_token.token_end_time),
            date_formatter
        )
        if token_creation_time <= now_time <= token_end_time:
            moltin_token = moltin_token.access_token
            return moltin_token
        else:
            moltin_token.active_token = False
            moltin_token.save()
            moltin_token = get_moltin_token(
                moltin_client_id,
                moltin_client_secret
            )
            return moltin_token
    else:
        moltin_token = get_moltin_token(moltin_client_id, moltin_client_secret)
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
        'amount'
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
        'Authorization': f'Bearer {moltin_token}',
        'Content-Type': 'application/json'
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


def get_all_flow(moltin_token):
    url = 'https://api.moltin.com/v2/flows/'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()


def create_flow(moltin_token, flow_status=True):
    url = 'https://api.moltin.com/v2/flows'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    json_data = {
        'data': {
            'type': 'flow',
            'name': 'Customer Address',
            'slug': 'customer_Address',
            'description': 'Customer Address',
            'enabled': flow_status
        },
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()


def create_entry(
        moltin_token,
        flow_name,
        fill_fields=dict
):
    url = f'https://api.moltin.com/v2/flows/{flow_name}/entries'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    json_data = {
        'data': fill_fields
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()


def get_all_entries(moltin_token, flow_name):
    url = f'https://api.moltin.com/v2/flows/{flow_name}/entries'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('data')


def get_enteries(moltin_token, slug):
    url = f'https://api.moltin.com/v2/flows/{slug}/entries'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('data')


def create_field(moltin_token):
    url = 'https://api.moltin.com/v2/fields'
    headers = {
        'Authorization': f'Bearer {moltin_token}'
    }
    data = {
        "data": {
            "type": "field",
            "name": "Deliveryman",
            "slug": "Deliveryman",
            "field_type": "string",
            "validation_rules": [],
            "description": "Deliveryman",
            "required": True,
            "default": 0,
            "enabled": True,
            "order": 1,
            "omit_null": False,
            "relationships": {
                "flow": {
                    "data": {
                        "type": "flow",
                        "id": "d8c36871-11d3-4e87-b1e8-224df3346383"
                    }
                }
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
