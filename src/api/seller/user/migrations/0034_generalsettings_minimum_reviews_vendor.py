# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-02 10:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0033_auto_20180731_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalsettings',
            name='minimum_reviews_vendor',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
    ]
