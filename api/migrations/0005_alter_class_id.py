# Generated by Django 5.1.7 on 2025-03-22 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_class_classenrollment_class_students_classteaching_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
