# Generated by Django 4.1.7 on 2023-10-05 20:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0011_order_orderitems"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="orderItems",
        ),
    ]