from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0004_user_must_change_password"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="id_expiry_date",
            field=models.DateField(
                blank=True,
                help_text="University ID expiry date. Expired IDs cannot login, register, or borrow.",
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="CampusStudent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("id_number", models.CharField(db_index=True, max_length=30, unique=True)),
                ("full_name", models.CharField(max_length=120)),
                ("phone", models.CharField(blank=True, default="", max_length=15)),
                ("department", models.CharField(blank=True, default="", max_length=70)),
                ("campus", models.CharField(blank=True, default="", max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "ACTIVE"), ("INACTIVE", "INACTIVE")],
                        default="ACTIVE",
                        max_length=20,
                    ),
                ),
                ("id_expiry_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "campus_students",
                "ordering": ["id_number"],
            },
        ),
    ]
