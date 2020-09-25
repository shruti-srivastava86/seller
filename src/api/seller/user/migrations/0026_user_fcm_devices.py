# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-19 09:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fcm_django', '0003_auto_20170313_1314'),
        ('user', '0025_searchterms_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fcm_devices',
            field=models.ManyToManyField(blank=True, related_name='fcm', to='fcm_django.FCMDevice'),
        ),
    ]
