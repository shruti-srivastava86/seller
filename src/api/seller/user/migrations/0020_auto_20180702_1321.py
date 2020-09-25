# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-02 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0019_auto_20180626_0726'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionLogView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qr_id', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField()),
                ('debit_amount', models.IntegerField()),
                ('debit_reason', models.PositiveSmallIntegerField(choices=[(0, 'Eater Reward'), (1, 'Points Expenditure'), (2, 'Eater Review'), (3, 'Eater Qr Scan'), (4, 'Vendor Redeemed')])),
                ('credit_amount', models.IntegerField()),
                ('credit_reason', models.PositiveSmallIntegerField(choices=[(0, 'Eater Reward'), (1, 'Points Expenditure'), (2, 'Eater Review'), (3, 'Eater Qr Scan'), (4, 'Vendor Redeemed')])),
            ],
            options={
                'managed': False,
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='reportvendor',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]
