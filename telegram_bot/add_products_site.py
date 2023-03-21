import json
from moltin_store import (
    get_moltin_token,
    create_product_store,
    create_file,
    create_file_relationship
)
from environs import Env


if __name__ == '__main__':
    with open('menu.json', 'r', encoding='utf-8') as menu_file:
        menu = menu_file.read()
    menu_json = json.loads(menu)
    env = Env()
    env.read_env()
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_token = get_moltin_token(moltin_client_id, moltin_client_secret)
    for product in menu_json:
        product_name = product.get('name')
        product_sku = str(product.get('id'))
        product_description = product.get('description')
        file_url = product.get('product_image').get('url')
        manage_stock = False
        product_status = 'live'
        product_amount = product.get('price')
        product_info = create_product_store(
                moltin_token,
                product_name,
                product_sku,
                product_description,
                manage_stock,
                product_amount,
                product_status
        )
        product_id = product_info.get('id')
        image_id = create_file(moltin_token, file_url).get('id')
        create_file_relationship(moltin_token, image_id, product_id)
