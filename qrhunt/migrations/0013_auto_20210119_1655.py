# Generated by Django 3.1.5 on 2021-01-19 08:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0012_assignedlocation_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='level',
            field=models.CharField(choices=[('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'), ('00', 'Not applicable')], default=django.utils.timezone.now, max_length=2),
            preserve_default=False,
        ),
    ]