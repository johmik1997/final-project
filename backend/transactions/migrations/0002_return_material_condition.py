from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="return",
            name="material_condition",
            field=models.CharField(
                choices=[("NEW", "NEW"), ("GOOD", "GOOD"), ("FAIR", "FAIR"), ("DAMAGED", "DAMAGED")],
                default="GOOD",
                max_length=20,
            ),
        ),
    ]
