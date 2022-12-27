import json
from environs import Env
from moltin_store import create_entry, get_moltin_token


if __name__ == '__main__':
    env = Env()
    env.read_env()
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_token = get_moltin_token(moltin_client_id, moltin_client_secret)
    with open('addresses.json', 'r', encoding='utf-8') as adresses_file:
        adresses = adresses_file.read()
    adresses_json = json.loads(adresses)
