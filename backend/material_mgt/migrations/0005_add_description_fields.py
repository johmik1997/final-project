"""Generated migration to add description fields to materials

"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("material_mgt", "0004_materialtransferrequest_rejection_reason_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="digitalmaterial",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="physicalmaterial",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
