# Generated by Django 3.1.5 on 2021-01-20 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0019_auto_20210120_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='block',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='fk_profile_block', to='qrhunt.block'),
        ),
    ]
