# Generated by Django 2.1.3 on 2018-11-27 04:28

import auction.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=auction.models.get_image_path),
        ),
    ]
