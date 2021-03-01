# Generated by Django 3.1.5 on 2021-03-01 19:41

from django.db import migrations
import qrhunt.utils


class Migration(migrations.Migration):

    dependencies = [
        ('qrhunt', '0040_photocomment_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='photosubmission',
            name='photo2',
            field=qrhunt.utils.ContentTypeRestrictedFileField(blank=True, null=True, upload_to=qrhunt.utils.update_filename),
        ),
        migrations.AddField(
            model_name='photosubmission',
            name='photo3',
            field=qrhunt.utils.ContentTypeRestrictedFileField(blank=True, null=True, upload_to=qrhunt.utils.update_filename),
        ),
    ]
