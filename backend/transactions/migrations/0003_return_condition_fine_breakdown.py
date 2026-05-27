from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0002_return_material_condition"),
    ]

    operations = [
        migrations.AddField(
            model_name="return",
            name="overdue_fine",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Fine calculated from overdue days \u00d7 daily rate",
                max_digits=10,
            ),
        ),
        migrations.AddField(
            model_name="return",
            name="condition_fine",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Fine calculated from material price \u00d7 condition penalty %",
                max_digits=10,
            ),
        ),
        migrations.AlterField(
            model_name="return",
            name="fine_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Total fine = overdue_fine + condition_fine",
                max_digits=10,
            ),
        ),
        migrations.AlterField(
            model_name="return",
            name="material_condition",
            field=models.CharField(
                choices=[
                    ("NEW", "NEW"),
                    ("GOOD", "GOOD"),
                    ("FAIR", "FAIR"),
                    ("DAMAGED", "DAMAGED"),
                    ("LOST", "LOST"),
                ],
                default="GOOD",
                max_length=20,
            ),
        ),
    ]
