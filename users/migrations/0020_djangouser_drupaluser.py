# Generated by Django 3.2.12 on 2022-09-26 12:41

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0019_add_new_user_groups"),
    ]

    operations = [
        migrations.CreateModel(
            name="DjangoUser",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("users.user",),
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="DrupalUser",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("users.user",),
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
