# Generated by Django 3.1.5 on 2021-01-21 03:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0021_auto_20210121_0042'),
    ]

    operations = [
        migrations.CreateModel(
            name='HpLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('time', models.DateTimeField(auto_now=True)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_hp_log_block', to='qrhunt.block')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_hp_log_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]