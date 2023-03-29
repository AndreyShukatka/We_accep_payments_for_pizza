import json
from We_accep_payments_for_pizza_django.settings import moltin_client_id, moltin_client_secret
from time import sleep
from moltin_store import create_entry, get_moltin_token
import requests

if __name__ == '__main__':
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
        fill_fields = {
            'type': 'entry',
            'Adress': pizzeria_address,
            'Alias': pizzeria_alias,
            'Longitude': pizzeria_longitude,
            'Latitude': pizzeria_latitude
        }
        try:
            create_entry(
                moltin_token,
                flow_name,
                fill_fields
            )
            sleep(2)
        except requests.exceptions.ConnectTimeout:
            continue