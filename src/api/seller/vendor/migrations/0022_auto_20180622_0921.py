# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-22 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0021_auto_20180620_1029'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='openinghours',
            options={'ordering': ['weekday'], 'verbose_name': 'Opening Hours', 'verbose_name_plural': 'Opening Hours'},
        ),
        migrations.AlterField(
            model_name='vendor',
            name='onboarding_stage',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Stage 1'), (2, 'Stage 2'), (3, 'Stage 3'), (4, 'Stage 4'), (5, 'Stage 5'), (6, 'Stage 6'), (7, 'Stage 7')], default=1),
        ),
    ]
