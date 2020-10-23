# Generated by Django 2.2.13 on 2020-10-15 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application_form", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hasoapplication",
            name="is_over_55",
            field=models.BooleanField(
                default=False, verbose_name="is applicant over 55 years old"
            ),
        ),
        migrations.AlterField(
            model_name="hasoapplication",
            name="running_number",
            field=models.CharField(
                max_length=255, verbose_name="right of occupancy ID"
            ),
        ),
        migrations.RenameField(
            model_name="hasoapplication",
            old_name="running_number",
            new_name="right_of_occupancy_id",
        ),
    ]
