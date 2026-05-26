from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("material_mgt", "0005_add_description_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="digitalmaterial",
            name="allow_downloadable",
            field=models.BooleanField(default=True),
        ),
    ]
