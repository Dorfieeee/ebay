# Generated by Django 3.1.3 on 2020-11-24 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20201124_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='curr_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10),
        ),
    ]
