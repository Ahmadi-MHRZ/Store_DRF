# Generated by Django 4.2.6 on 2024-08-20 21:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_category_top_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='datetime_created',
        ),
        migrations.AlterField(
            model_name='product',
            name='inventory',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
