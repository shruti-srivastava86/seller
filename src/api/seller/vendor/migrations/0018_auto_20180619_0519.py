# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-19 05:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0017_auto_20180503_0541'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='card',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='business',
            name='cash',
            field=models.BooleanField(default=False),
        ),
    ]
