from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from event.models import Category, Event
from datetime import datetime, timedelta

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None

PREVIEW_COLORS = {
    'concert': ('#2d1b4e', '#e85d4c'),
    'exhibition': ('#1a2a3a', '#5b8def'),
    'festival': ('#1f3d2b', '#f5a623'),
    'theater': ('#3d1f2f', '#d946a8'),
    'masterclass': ('#2a2f1a', '#7bc96f'),
    'default': ('#1a2332', '#8b9cb3'),
}

EVENT_PREVIEWS = {
    'Рок-концерт': 'concert',
    'Выставка современного искусства': 'exhibition',
    'Городской джаз-фестиваль': 'festival',
    'Спектакль «Городские истории»': 'theater',
    'Мастер-класс по акварели': 'masterclass',
}


class Command(BaseCommand):
    def _build_preview_image(self, slug):
        static_dir = Path(settings.BASE_DIR) / 'event' / 'static' / 'event' / 'img' / 'previews'
        static_dir.mkdir(parents=True, exist_ok=True)
        static_path = static_dir / f'{slug}.jpg'

        if static_path.exists():
            return static_path.read_bytes()

        if Image is None:
            raise RuntimeError('Установите Pillow: python -m pip install Pillow')

        color_top, color_bottom = PREVIEW_COLORS.get(slug, PREVIEW_COLORS['default'])
        image = Image.new('RGB', (800, 500), color_top)
        draw = ImageDraw.Draw(image)

        for y in range(500):
            ratio = y / 499
            top = tuple(int(color_top[i:i + 2], 16) for i in (1, 3, 5))
            bottom = tuple(int(color_bottom[i:i + 2], 16) for i in (1, 3, 5))
            row_color = tuple(
                int(top[channel] + (bottom[channel] - top[channel]) * ratio)
                for channel in range(3)
            )
            draw.line([(0, y), (800, y)], fill=row_color)

        draw.rounded_rectangle((40, 360, 760, 460), radius=24, fill=(15, 20, 25, 180))
        draw.text((60, 390), slug.replace('-', ' ').title(), fill='#e8edf4')

        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        image_bytes = buffer.getvalue()
        static_path.write_bytes(image_bytes)
        return image_bytes

    def _attach_preview(self, event, slug):
        if event.preview:
            return

        image_data = self._build_preview_image(slug)
        filename = f'{slug}-{event.pk}.jpg'
        event.preview.save(filename, ContentFile(image_data), save=True)
        self.stdout.write(f'Превью добавлено: {event.title}')

    def handle(self, *args, **kwargs):
        admin, created = User.objects.get_or_create(username='admin')
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('Администратор создан')
        else:
            self.stdout.write('Администратор уже существует')

        cat1, created1 = Category.objects.get_or_create(
            slug='concert',
            defaults={'name': 'Концерт'}
        )
        if created1:
            self.stdout.write('Категория "Концерт" создана')
        else:
            self.stdout.write('Категория "Концерт" уже существует')

        cat2, created2 = Category.objects.get_or_create(
            slug='exhibition',
            defaults={'name': 'Выставка'}
        )
        if created2:
            self.stdout.write('Категория "Выставка" создана')
        else:
            self.stdout.write('Категория "Выставка" уже существует')

        cat3, created3 = Category.objects.get_or_create(
            slug='festival',
            defaults={'name': 'Фестиваль'}
        )
        if created3:
            self.stdout.write('Категория "Фестиваль" создана')

        cat4, created4 = Category.objects.get_or_create(
            slug='theater',
            defaults={'name': 'Спектакль'}
        )
        if created4:
            self.stdout.write('Категория "Спектакль" создана')

        cat5, created5 = Category.objects.get_or_create(
            slug='masterclass',
            defaults={'name': 'Мастер-класс'}
        )
        if created5:
            self.stdout.write('Категория "Мастер-класс" создана')

        event1, created_e1 = Event.objects.get_or_create(
            title='Рок-концерт',
            defaults={
                'description': 'Выступление местных групп',
                'date': datetime.now() + timedelta(days=5),
                'location': 'Клуб "Город"',
                'category': cat1,
                'price': 500,
                'created_by': admin,
            }
        )
        if created_e1:
            self.stdout.write('Событие "Рок-концерт" создано')
        else:
            self.stdout.write('Событие "Рок-концерт" уже существует')

        event2, created_e2 = Event.objects.get_or_create(
            title='Выставка современного искусства',
            defaults={
                'description': 'Работы молодых художников',
                'date': datetime.now() + timedelta(days=10),
                'location': 'Лофт "Этажи"',
                'category': cat2,
                'price': 0,
                'created_by': admin,
            }
        )
        if created_e2:
            self.stdout.write('Событие "Выставка современного искусства" создано')
        else:
            self.stdout.write('Событие "Выставка современного искусства" уже существует')

        event3, created_e3 = Event.objects.get_or_create(
            title='Городской джаз-фестиваль',
            defaults={
                'description': 'Три дня живой музыки на открытой площадке',
                'date': datetime.now() + timedelta(days=14),
                'location': 'Парк Горького',
                'category': cat3,
                'price': 1200,
                'created_by': admin,
            }
        )
        if created_e3:
            self.stdout.write('Событие "Городской джаз-фестиваль" создано')

        event4, created_e4 = Event.objects.get_or_create(
            title='Спектакль «Городские истории»',
            defaults={
                'description': 'Современная драма в двух действиях',
                'date': datetime.now() + timedelta(days=7),
                'location': 'Театр на Таганке',
                'category': cat4,
                'price': 800,
                'created_by': admin,
            }
        )
        if created_e4:
            self.stdout.write('Событие "Спектакль «Городские истории»" создано')

        event5, created_e5 = Event.objects.get_or_create(
            title='Мастер-класс по акварели',
            defaults={
                'description': 'Занятие для начинающих художников',
                'date': datetime.now() + timedelta(days=3),
                'location': 'Арт-студия «Палитра»',
                'category': cat5,
                'price': 0,
                'created_by': admin,
            }
        )
        if created_e5:
            self.stdout.write('Событие "Мастер-класс по акварели" создано')

        for event in Event.objects.select_related('category'):
            slug = EVENT_PREVIEWS.get(event.title, event.category.slug)
            self._attach_preview(event, slug)

        self.stdout.write(self.style.SUCCESS('Готово! База данных проверена и заполнена необходимыми данными.'))
