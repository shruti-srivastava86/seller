# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-25 11:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eater', '0010_eater_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eater',
            name='facebook_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True, unique=True),
        ),
    ]
