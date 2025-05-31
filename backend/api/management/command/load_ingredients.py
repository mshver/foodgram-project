import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from api.models import Component  # Изменено с Ingredient на Component

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Загрузка компонентов из JSON файла'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='components.json', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            with open(os.path.join(DATA_ROOT, options['filename']), 'r',
                      encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    try:
                        # Используем новые названия полей: title и unit
                        Component.objects.create(
                            title=item["name"],
                            unit=item["measurement_unit"]
                        )
                    except IntegrityError:
                        self.stdout.write(self.style.WARNING(
                            f'Компонент {item["name"]} ({item["measurement_unit"]}) уже существует'
                        ))

        except FileNotFoundError:
            raise CommandError(f'Файл {options["filename"]} не найден в директории data')