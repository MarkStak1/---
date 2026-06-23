from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_registration_amount_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='preview',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='events/previews/',
                verbose_name='Фото-превью',
            ),
        ),
    ]
