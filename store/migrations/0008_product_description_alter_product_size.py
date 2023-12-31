# Generated by Django 4.1.7 on 2023-09-23 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0007_order_paid"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="description",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="size",
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]
