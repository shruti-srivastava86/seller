# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-13 11:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0036_auto_20180809_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportvendor',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]
