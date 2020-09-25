# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-20 09:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0018_auto_20180619_0519'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='business',
            name='vendor_busi_cashles_123afb_idx',
        ),
        migrations.RemoveField(
            model_name='business',
            name='cashless',
        ),
        migrations.AddIndex(
            model_name='business',
            index=models.Index(fields=['cash'], name='vendor_busi_cash_9f988e_idx'),
        ),
        migrations.AddIndex(
            model_name='business',
            index=models.Index(fields=['card'], name='vendor_busi_card_25b875_idx'),
        ),
    ]
