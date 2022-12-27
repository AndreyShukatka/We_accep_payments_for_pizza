import json
from time import sleep
from environs import Env
from moltin_store import create_entry, get_moltin_token
import requests

if __name__ == '__main__':
    env = Env()
    env.read_env()
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_token = get_moltin_token(moltin_client_id, moltin_client_secret)
    flow_name = 'Pizzeria'
    with open('addresses.json', 'r', encoding='utf-8') as adresses_file:
        adresses = adresses_file.read()
    adresses_json = json.loads(adresses)
    for adresse in adresses_json:
        pizzeria_address = adresse.get('address').get('full')
        pizzeria_alias = adresse.get('alias')
        pizzeria_longitude = adresse.get('coordinates').get('lon')
        pizzeria_latitude =adresse.get('coordinates').get('lat')
        try:
            create_entry(
                moltin_token,
                pizzeria_address,
                pizzeria_alias,
                pizzeria_longitude,
                pizzeria_latitude,
                flow_name
            )
            sleep(2)
        except requests.exceptions.ConnectTimeout:
            continue