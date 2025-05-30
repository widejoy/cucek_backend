# Generated by Django 5.1.7 on 2025-03-31 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_placementprofile_is_placement_coordinator"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlacementCompany",
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
                ("name", models.CharField(max_length=200)),
                ("job_description", models.TextField()),
                (
                    "min_cgpa",
                    models.DecimalField(decimal_places=2, max_digits=2, null=True),
                ),
                (
                    "min_10th",
                    models.DecimalField(decimal_places=2, max_digits=3, null=True),
                ),
                (
                    "min_12th",
                    models.DecimalField(decimal_places=2, max_digits=3, null=True),
                ),
                ("max_backlogs", models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name="placementprofile",
            name="cgpa",
            field=models.DecimalField(decimal_places=2, max_digits=2),
        ),
    ]
