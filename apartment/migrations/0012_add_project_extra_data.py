# Generated by Django 3.2.12 on 2022-05-27 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("apartment", "0011_delete_project_and_apartment"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectExtraData",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "project_uuid",
                    models.UUIDField(unique=True, verbose_name="project UUID"),
                ),
                (
                    "offer_message_intro",
                    models.TextField(blank=True, verbose_name="offer message intro"),
                ),
                (
                    "offer_message_content",
                    models.TextField(blank=True, verbose_name="offer message content"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
