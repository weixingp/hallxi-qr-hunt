# Generated by Django 3.1.5 on 2021-01-21 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0022_hplog'),
    ]

    operations = [
        migrations.AddField(
            model_name='hplog',
            name='reason',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
