# Generated by Django 4.1.7 on 2023-08-23 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_product_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="size",
            field=models.CharField(
                choices=[("small", "Small"), ("large", "Large")],
                default="small",
                max_length=50,
            ),
        ),
    ]