"""Management command to initialize email templates."""
from django.core.management.base import BaseCommand
from user_mgt.models import EmailTemplate


class Command(BaseCommand):
    help = 'Initialize default email templates for library notifications'

    def handle(self, *args, **options):
        templates_data = [
            {
                'template_type': 'OVERDUE',
                'name': 'Overdue Material Notification',
                'subject': 'Library Notice: Borrowed Material Is Overdue',
                'body_html': '''<html><body><h2>Overdue Material Reminder</h2>
<p>Dear {member_name},</p>
<p>This is a reminder that your borrowed material is <strong>OVERDUE</strong>.</p>
<p><strong>Material:</strong> {material_title} by {material_author}</p>
<p><strong>Due Date:</strong> {due_date}</p>
<p><strong>Days Overdue:</strong> {overdue_days}</p>
<p>Please return this material as soon as possible to avoid additional fines.</p>
<p>Library: {library_name}</p></body></html>''',
                'body_text': '''Dear {member_name},

This is a reminder that your borrowed material is OVERDUE.

Material: {material_title} by {material_author}
Due Date: {due_date}
Days Overdue: {overdue_days}

Please return this material as soon as possible to avoid additional fines.

Library: {library_name}'''
            },
            {
                'template_type': 'RESERVED_AVAILABLE',
                'name': 'Reserved Material Available Notification',
                'subject': 'Library Update: Your Reserved Material Is Now Available',
                'body_html': '''<html><body><h2>Reserved Material Available</h2>
<p>Dear {member_name},</p>
<p>Good news! The material you reserved is now <strong>AVAILABLE</strong>.</p>
<p><strong>Material:</strong> {material_title} by {material_author}</p>
<p>Please visit the library promptly to borrow this material.</p>
<p>Library: {library_name}</p></body></html>''',
                'body_text': '''Dear {member_name},

Good news! The material you reserved is now AVAILABLE.

Material: {material_title} by {material_author}

Please visit the library promptly to borrow this material.

Library: {library_name}'''
            },
            {
                'template_type': 'BORROW_CONFIRMATION',
                'name': 'Borrow Confirmation',
                'subject': 'Library Confirmation: Material Borrowed Successfully',
                'body_html': '''<html><body><h2>Borrow Confirmation</h2>
<p>Dear {member_name},</p>
<p>Your material has been successfully borrowed.</p>
<p><strong>Material:</strong> {material_title} by {material_author}</p>
<p><strong>Due Date:</strong> {due_date}</p>
<p>Please ensure to return this material by the due date to avoid fines.</p>
<p>Library: {library_name}</p></body></html>''',
                'body_text': '''Dear {member_name},

Your material has been successfully borrowed.

Material: {material_title} by {material_author}
Due Date: {due_date}

Please ensure to return this material by the due date to avoid fines.

Library: {library_name}'''
            },
            {
                'template_type': 'RETURN_CONFIRMATION',
                'name': 'Return Confirmation',
                'subject': 'Library Confirmation: Material Returned Successfully',
                'body_html': '''<html><body><h2>Return Confirmation</h2>
<p>Dear {member_name},</p>
<p>Your material has been successfully returned.</p>
<p><strong>Material:</strong> {material_title} by {material_author}</p>
<p><strong>Return Date:</strong> {return_date}</p>
<p><strong>Fine:</strong> {fine_amount}</p>
<p>Thank you for using our library!</p>
<p>Library: {library_name}</p></body></html>''',
                'body_text': '''Dear {member_name},

Your material has been successfully returned.

Material: {material_title} by {material_author}
Return Date: {return_date}
Fine: {fine_amount}

Thank you for using our library!

Library: {library_name}'''
            },
        ]

        for template_data in templates_data:
            template, created = EmailTemplate.objects.get_or_create(
                template_type=template_data['template_type'],
                defaults=template_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(
                self.style.SUCCESS(f'{status}: {template.name}')
            )

        self.stdout.write(
            self.style.SUCCESS('Email templates initialized successfully!')
        )
