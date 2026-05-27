from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0003_return_condition_fine_breakdown"),
    ]

    operations = [
        migrations.AddField(
            model_name="return",
            name="policy_percentage_used",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="The condition penalty % from Library Policy used at return time",
                max_digits=6,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="return",
            name="material_price_used",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="The material price used at return time for condition fine calculation",
                max_digits=10,
                null=True,
            ),
        ),
    ]
