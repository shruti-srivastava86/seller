# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-01 13:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import seller.eater.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('dish', '0002_auto_20180301_1313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Eater',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('home_market', models.CharField(max_length=255)),
                ('dietary_preference', models.ManyToManyField(blank=True, related_name='eaters', to='dish.Dietary')),
            ],
            options={
                'verbose_name_plural': 'Eater',
                'verbose_name': 'Eater',
            },
            bases=('user.user',),
            managers=[
                ('objects', seller.eater.managers.EaterUserManager()),
            ],
        ),
        migrations.AddIndex(
            model_name='eater',
            index=models.Index(fields=['home_market'], name='eater_eater_home_ma_743266_idx'),
        ),
    ]
