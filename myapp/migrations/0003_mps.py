# Generated by Django 5.1.2 on 2024-10-11 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0002_allocationcomposition_billofmaterial_inventory_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MPS",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "material_code",
                    models.CharField(max_length=10, verbose_name="物料号"),
                ),
                ("quantity", models.IntegerField(verbose_name="数量")),
                ("date", models.DateField(verbose_name="日期")),
            ],
        ),
    ]
