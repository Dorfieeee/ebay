# Generated by Django 3.1.3 on 2020-11-25 11:50

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20201124_1514'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='watchlist',
            managers=[
                ('active', django.db.models.manager.Manager()),
            ],
        ),
    ]
