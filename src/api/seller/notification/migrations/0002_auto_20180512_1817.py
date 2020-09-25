# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-12 18:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EaterPreference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('marketing', models.BooleanField(default=True)),
                ('review', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Eater Preference',
                'verbose_name': 'Eater Preference',
            },
        ),
        migrations.AddIndex(
            model_name='eaterpreference',
            index=models.Index(fields=['marketing'], name='notificatio_marketi_04ac19_idx'),
        ),
        migrations.AddIndex(
            model_name='eaterpreference',
            index=models.Index(fields=['review'], name='notificatio_review_37434b_idx'),
        ),
    ]
