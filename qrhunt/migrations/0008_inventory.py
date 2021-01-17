# Generated by Django 3.1.5 on 2021-01-17 15:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0007_item_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_used', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_item', to='qrhunt.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
