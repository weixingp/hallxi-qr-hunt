# Generated by Django 3.1.5 on 2021-01-17 15:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0009_auto_20210117_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_inventory_item', to='qrhunt.item'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_inventory_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='AssignedQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now=True)),
                ('has_answered', models.BooleanField(default=False)),
                ('answered_time', models.DateTimeField(blank=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_assigned_question_question', to='qrhunt.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_assigned_question_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]