# Generated by Django 3.1.5 on 2021-01-09 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0002_user_is_registered'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='room_no',
            field=models.CharField(default='', max_length=30, null=True),
        ),
    ]
