# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-25 09:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_auto_20180620_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notes',
            field=models.TextField(blank=True, help_text='\n        Hawkker Team Notes.\n        These are for staff use only and are not displayed to\n        any other users', null=True),
        ),
    ]
