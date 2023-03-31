from django.core.management.base import BaseCommand
from django.conf import settings
from telegram_bot.moltin_store import (
    get_moltin_token,
    create_product_store,
    del_product_store,
    get_all_products,
    create_inventory_store,
    create_file_relationship,
    create_file, create_entry,
    create_flow,
    create_field,
    get_all_flow,
    get_enteries
)


class Command(BaseCommand):
    help = 'Start Moltin Store'

    def add_arguments(self, parser):
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
        parser.add_argument(
            '--create_entry',
            help='Создать модель',
            action="store_true"
        )
        parser.add_argument(
            '--create_flow',
            help='Создать модель',
            action="store_true"
        )
        parser.add_argument(
            '--create_field',
            help='Создать поле',
            action="store_true"
        )
        parser.add_argument(
            '--get_all_flow',
            help='Создать поле',
            action="store_true"
        )
        parser.add_argument(
            '--get_enteries',
            help='Поиск поля',
            action='store_true'
        )

    def handle(self, *args, **options):
        moltin_token = get_moltin_token(
            settings.moltin_client_id,
            settings.moltin_client_secret
        )
        if options['create_product']:
            product_name = options['product_name']
            sku = options['sku']
            description = options['description']
            manage_stock = options['manage_stock']
            amount = options['amount']
            product_status = options['product_status']
            create_product_store(
                moltin_token,
                product_name,
                sku,
                description,
                manage_stock,
                amount,
                product_status
            )
        elif options['del_product']:
            product_id = options['product_id']
            del_product_store(moltin_token, product_id)
        elif options['get_all_products']:
            print(get_all_products(moltin_token))
        elif options['create_inventory_store']:
            quantity = options['quantity']
            product_id = options['product_id']
            create_inventory_store(moltin_token, quantity, product_id)
        elif options['create_file_relationship']:
            product_id = options['product_id']
            image_id = options['image_id']
            create_file_relationship(moltin_token, image_id, product_id)
        elif options['create_file']:
            file_url = options['file_url']
            create_file(moltin_token, file_url)
        elif options['create_entry']:
            create_entry(
                moltin_token,
                flow_name='customer_Address'
            )
        elif options['create_flow']:
            create_flow(moltin_token, flow_status=True)
        elif options['create_field']:
            create_field(moltin_token)
        elif options['get_all_flow']:
            get_all_flow(moltin_token)
        elif options['get_enteries']:
            get_enteries(moltin_token)
