# Generated by Django 3.1.5 on 2021-01-17 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0008_inventory'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventory',
            options={'verbose_name_plural': 'Inventories'},
        ),
        migrations.AddField(
            model_name='inventory',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]