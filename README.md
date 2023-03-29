# Pizza bot

## Telegram

Бот Telegram предоставляет доступ к пиццерии. Вы можете выбрать пиццу, какую хотите, получить описание выбранной пиццы с
изображением, добавить пиццу в корзину, удалить из корзины и отправить запрос на оплату. Этот бот использует API
сервиса [Elasticpath](https://www.elasticpath.com/) (до этого сервис назывался Molton).

Все методы CRUD работали через
API [documentation.elasticpath](https://documentation.elasticpath.com/commerce-cloud/docs/api/index.html).


### Начать использовать

Прежде чем начать, убедитесь, что вы выполнили следующие требования:
- Язык программирования [Python 3.11](https://www.python.org/)
- Установить виртуальную среду
```shell
python3 -m venv env
source env/bin/activate
```
- Установить зависимости 
```
- pip install -r requirements.txt
```
- Создать базу данных Django:
```shell
python3 manage.py makemigrations
python3 manage.py migrate
```
- Создать суперюзера:
```shell
python3 manage.py createsuperuser
```
- Оболочка Telegram API [python-telegram-bot V12.8.0](https://github.com/python-telegram-bot/python-telegram-bot/tree/v12.8.0)

Вы должны создать аккаунты на следующих ресурсах:
- Интернет-магазин в [Elasticpath](https://www.elasticpath.com/).
- Telegram-бот через `@BotFather`

Объявите переменные окружения по умолчанию в файле `.env`:

- `DJANGO_SECRET_KEY` - Ваш секретный ключ джанго
- `MOLTIN_CLIENT_ID` - идентификатор клиента Elasticpath.
- `MOLTIN_CLIENT_SECRET` - секретный токен клиента Elasticpath.
- `TGM_TOKEN` - токен вашего телеграм-бота.
- `YANDEX_API_KEY` - ключ доступа к API карт Яндекса.
- `BANK_TOKEN` - токен для доступа к вашему платежному сервису.
- `PAYLOAD` - ваша секретная полезная нагрузка для проверки перевода.

### Запуск
- Для запуска пропишите
```shell
python2 pizza_bot.py
```

# Работа с магазином
### Вывести все товары в магазине в консоль
```shell
python moltin_store.py --get_all_products 
```


### Добавить продукт в магазин
```shell
python moltin_store.py --create_product --product_name <Название продукта> --sku <SKU предмета> --description <Описание продукта> --amount <Цена продукта>
```

### Пополнить запасы на складе
```shell
python moltin_store.py --create_inventory_store --product_id <ID продукта> --quantity <Количество>
```

### Удалить продукт из магазина
```shell
python moltin_store.py --del_product --product_id <ID продукта>
```

### Привязать фотографию к товару
- Загружаем картинку через [сайт]()
- Она появляется в файлах, берем от туда ID
![img.png](img.png)

```shell
python moltin_store.py --create_file_relationship --image_id <ID фотографии с сайта> --product_id <ID продукта>
```
