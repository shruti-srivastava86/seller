# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-12 12:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eater', '0006_auto_20180529_1154'),
        ('user', '0015_auto_20180529_0601'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportEater',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
                ('eater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_eater', to='eater.Eater')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
