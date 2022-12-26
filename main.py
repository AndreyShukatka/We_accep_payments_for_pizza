import json
from environs import Env


def main():
    env = Env()
    env.read_env()

    with open('addresses.json', 'r', encoding='utf-8') as adresses_file:
        adresses = adresses_file.read()
    adresses_json = json.loads(adresses)
    print(adresses_json)
    with open('menu.json', 'r', encoding='utf-8') as menu_file:
        menu = menu_file.read()
    menu_json = json.loads(menu)
    print(menu_json)
if __name__ == '__main__':
    main()