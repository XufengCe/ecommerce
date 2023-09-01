# Generated by Django 4.1.7 on 2023-08-30 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_product_size"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=7, null=True
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="digital",
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="size",
            field=models.CharField(
                choices=[
                    ("small", "Small"),
                    ("large", "Large"),
                    ("combo-small", "Combo-Samll"),
                    ("combo-large", "Combo-Large"),
                ],
                default="small",
                max_length=50,
            ),
        ),
    ]
