# Generated by Django 4.0.1 on 2023-06-27 18:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_roomlogs_delete_roomusers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roomlogs',
            name='data_sended',
        ),
        migrations.AddField(
            model_name='roomlogs',
            name='data_joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 27, 20, 40, 57, 321665)),
        ),
        migrations.AddField(
            model_name='roomlogs',
            name='data_left',
            field=models.DateTimeField(blank=True, default=None),
        ),
    ]