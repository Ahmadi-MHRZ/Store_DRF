# Generated by Django 4.2.6 on 2024-08-20 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_remove_address_address_detail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='datetime_created',
        ),
    ]
