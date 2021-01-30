# Generated by Django 3.1.5 on 2021-01-30 04:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0030_assignedlootbox'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignedlootbox',
            options={'verbose_name_plural': 'Assigned loot boxes'},
        ),
        migrations.RemoveField(
            model_name='assignedlootbox',
            name='item',
        ),
        migrations.AddField(
            model_name='assignedlootbox',
            name='has_opened',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='AssignedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_used', models.BooleanField(blank=True, null=True)),
                ('used_time', models.DateTimeField(blank=True, null=True)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fk_assigned_item_item', to='qrhunt.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_assigned_item_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='assignedlootbox',
            name='assigned_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fk_assigned_loot_box_assigned_item', to='qrhunt.assigneditem'),
        ),
    ]
