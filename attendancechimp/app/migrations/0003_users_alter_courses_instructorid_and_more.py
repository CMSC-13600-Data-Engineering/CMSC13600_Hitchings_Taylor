# Generated by Django 4.1.7 on 2023-04-03 02:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0002_rename_first_name_user_name_remove_user_last_name_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Users",
            fields=[
                ("userid", models.AutoField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(blank=True, max_length=50, null=True)),
                ("last_name", models.CharField(blank=True, max_length=50, null=True)),
                ("email", models.CharField(blank=True, max_length=50, null=True)),
                ("user_type", models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name="courses",
            name="instructorid",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="studentid",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.DeleteModel(
            name="User",
        ),
    ]
