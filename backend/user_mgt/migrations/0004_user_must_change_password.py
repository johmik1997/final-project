from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0003_alter_notification_borrow_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="must_change_password",
            field=models.BooleanField(default=False),
        ),
    ]
