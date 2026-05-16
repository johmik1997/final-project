# Generated migration for email models

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('template_type', models.CharField(choices=[('OVERDUE', 'Overdue Notification'), ('RESERVED_AVAILABLE', 'Reserved Material Available'), ('BORROW_CONFIRMATION', 'Borrow Confirmation'), ('RETURN_CONFIRMATION', 'Return Confirmation'), ('CUSTOM', 'Custom Template')], max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=500)),
                ('body_html', models.TextField()),
                ('body_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['template_type'],
            },
        ),
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('recipient_email', models.EmailField(max_length=254)),
                ('email_type', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=500)),
                ('status', models.CharField(choices=[('SENT', 'Sent'), ('FAILED', 'Failed'), ('PENDING', 'Pending')], default='PENDING', max_length=20)),
                ('error_message', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('borrow_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_logs', to='transactions.borrow')),
                ('recipient_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_logs', to='backend.user')),
                ('reservation_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_logs', to='transactions.reservation')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logs', to='backend.emailtemplate')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='emaillog',
            index=models.Index(fields=['recipient_email', '-created_at'], name='backend_emaillog_recipient_email_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='emaillog',
            index=models.Index(fields=['status', '-created_at'], name='backend_emaillog_status_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='emaillog',
            index=models.Index(fields=['email_type', '-created_at'], name='backend_emaillog_email_type_created_at_idx'),
        ),
    ]
