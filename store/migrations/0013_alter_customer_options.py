# Generated by Django 5.1.1 on 2024-09-13 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_remove_customer_email_remove_customer_first_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'permissions': [('send_privet_email', 'Can send private to user by the button')]},
        ),
    ]
