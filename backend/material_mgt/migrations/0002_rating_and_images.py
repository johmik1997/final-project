# Generated migration for Rating model and image fields

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('material_mgt', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add image fields to materials
        migrations.AddField(
            model_name='digitalmaterial',
            name='image',
            field=models.ImageField(blank=True, help_text='Optional custom image for the material', null=True, upload_to='material_images/digital/'),
        ),
        migrations.AddField(
            model_name='physicalmaterial',
            name='image',
            field=models.ImageField(blank=True, help_text='Optional custom image for the material', null=True, upload_to='material_images/physical/'),
        ),
        # Create Rating model
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('rating', models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])),
                ('review', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('digital_material', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='material_mgt.digitalmaterial')),
                ('physical_material', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='material_mgt.physicalmaterial')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['user', 'updated_at'], name='material_mgt_rating_user_updated_at_idx'),
        ),
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['physical_material', 'updated_at'], name='material_mgt_rating_physical_updated_at_idx'),
        ),
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['digital_material', 'updated_at'], name='material_mgt_rating_digital_updated_at_idx'),
        ),
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['rating'], name='material_mgt_rating_rating_idx'),
        ),
        # Add constraints
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.CheckConstraint(condition=models.Q(('physical_material__isnull', False), ('digital_material__isnull', True)) | models.Q(('physical_material__isnull', True), ('digital_material__isnull', False)), name='rating_exactly_one_material'),
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.CheckConstraint(condition=models.Q(('rating__gte', 1), ('rating__lte', 5)), name='rating_range'),
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(condition=models.Q(('physical_material__isnull', False)), fields=['user', 'physical_material'], name='rating_unique_user_physical'),
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(condition=models.Q(('digital_material__isnull', False)), fields=['user', 'digital_material'], name='rating_unique_user_digital'),
        ),
    ]
