from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("material_mgt", "0007_add_digital_material_access_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="materialtransferrequest",
            name="destination_location",
            field=models.CharField(
                choices=[("STACK", "STACK"), ("SHELF", "SHELF")],
                default="SHELF",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="materialtransferrequest",
            name="source_location",
            field=models.CharField(
                choices=[("STACK", "STACK"), ("SHELF", "SHELF")],
                default="STACK",
                max_length=20,
            ),
        ),
    ]
