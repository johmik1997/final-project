"""Email service for library notifications."""
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import EmailTemplate, EmailLog, User

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending library notification emails."""
    
    @staticmethod
    def get_template(template_type):
        """Retrieve an email template by type."""
        try:
            return EmailTemplate.objects.get(template_type=template_type)
        except EmailTemplate.DoesNotExist:
            logger.warning(f"Email template '{template_type}' not found")
            return None
    
    @staticmethod
    def render_template(template, context):
        """Render template with given context."""
        if not template:
            return None, None
        
        subject = template.subject.format(**context)
        body_html = template.body_html.format(**context)
        body_text = template.body_text.format(**context)
        
        return subject, body_html, body_text
    
    @staticmethod
    def send_email(
        recipient_email,
        subject,
        body_html,
        body_text=None,
        recipient_user=None,
        email_type="CUSTOM",
        template=None,
        borrow=None,
        reservation=None
    ):
        """
        Send an email and log it.
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body (optional)
            recipient_user: User object (optional)
            email_type: Type of email for logging
            template: EmailTemplate object (optional)
            borrow: Related Borrow object (optional)
            reservation: Related Reservation object (optional)
        
        Returns:
            EmailLog object or None if failed
        """
        if not body_text:
            body_text = body_html.replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n")
        
        email_log = EmailLog.objects.create(
            recipient_email=recipient_email,
            recipient_user=recipient_user,
            email_type=email_type,
            subject=subject,
            template=template,
            status="PENDING",
            borrow_id=borrow.id if borrow else None,
            reservation_id=reservation.id if reservation else None
        )
        
        try:
            send_mail(
                subject=subject,
                message=body_text,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[recipient_email],
                html_message=body_html,
                fail_silently=False,
            )
            email_log.status = "SENT"
            email_log.sent_at = timezone.now()
            logger.info(f"Email sent successfully: {email_log.id}")
        except Exception as exc:
            email_log.status = "FAILED"
            email_log.error_message = str(exc)
            logger.error(f"Failed to send email: {exc}")
        
        email_log.save()
        return email_log
    
    @classmethod
    def send_overdue_notification(cls, borrow):
        """Send overdue material notification."""
        template = cls.get_template('OVERDUE')
        if not template:
            logger.warning("Overdue email template not found")
            return None
        
        member = borrow.member
        material = borrow.material
        now = timezone.now()
        overdue_days = (now.date() - borrow.due_date.date()).days
        
        context = {
            'member_name': member.first_name or member.id_number,
            'material_title': material.title,
            'material_author': material.author,
            'due_date': borrow.due_date.date().isoformat(),
            'overdue_days': overdue_days,
            'library_name': material.library.name if material.library else 'Library',
        }
        
        subject, body_html, body_text = cls.render_template(template, context)
        if not subject:
            return None
        
        return cls.send_email(
            recipient_email=member.email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            recipient_user=member,
            email_type='OVERDUE',
            template=template,
            borrow=borrow
        )
    
    @classmethod
    def send_reserved_available_notification(cls, reservation):
        """Send reserved material available notification."""
        template = cls.get_template('RESERVED_AVAILABLE')
        if not template:
            logger.warning("Reserved available email template not found")
            return None
        
        member = reservation.member
        material = reservation.material_id
        
        context = {
            'member_name': member.first_name or member.id_number,
            'material_title': material.title,
            'material_author': material.author,
            'library_name': material.library.name if material.library else 'Library',
        }
        
        subject, body_html, body_text = cls.render_template(template, context)
        if not subject:
            return None
        
        return cls.send_email(
            recipient_email=member.email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            recipient_user=member,
            email_type='RESERVED_AVAILABLE',
            template=template,
            reservation=reservation
        )
    
    @classmethod
    def send_borrow_confirmation(cls, borrow):
        """Send borrow confirmation email."""
        template = cls.get_template('BORROW_CONFIRMATION')
        if not template:
            logger.warning("Borrow confirmation email template not found")
            return None
        
        member = borrow.member
        material = borrow.material
        
        context = {
            'member_name': member.first_name or member.id_number,
            'material_title': material.title,
            'material_author': material.author,
            'due_date': borrow.due_date.date().isoformat(),
            'library_name': material.library.name if material.library else 'Library',
        }
        
        subject, body_html, body_text = cls.render_template(template, context)
        if not subject:
            return None
        
        return cls.send_email(
            recipient_email=member.email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            recipient_user=member,
            email_type='BORROW_CONFIRMATION',
            template=template,
            borrow=borrow
        )
    
    @classmethod
    def send_return_confirmation(cls, return_obj):
        """Send return confirmation email."""
        template = cls.get_template('RETURN_CONFIRMATION')
        if not template:
            logger.warning("Return confirmation email template not found")
            return None
        
        borrow = return_obj.borrow
        member = borrow.member
        material = borrow.material
        
        context = {
            'member_name': member.first_name or member.id_number,
            'material_title': material.title,
            'material_author': material.author,
            'return_date': return_obj.return_date.date().isoformat(),
            'fine_amount': return_obj.fine_amount,
            'library_name': material.library.name if material.library else 'Library',
        }
        
        subject, body_html, body_text = cls.render_template(template, context)
        if not subject:
            return None
        
        return cls.send_email(
            recipient_email=member.email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            recipient_user=member,
            email_type='RETURN_CONFIRMATION',
            template=template,
            borrow=borrow
        )
