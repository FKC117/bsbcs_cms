"""Django signals for the website app.

Handles post-save operations like sending approval/rejection emails
when a Member's approval_status changes.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Member
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Member)
def send_member_approval_email(sender, instance, created, update_fields, **kwargs):
    """Send approval/rejection email to user when Member approval_status changes.
    
    Listens for Member.post_save signal. If approval_status is approved or rejected,
    sends an appropriate email to the user's profile email address.
    
    Args:
        sender: The Member model class
        instance: The Member instance being saved
        created: Boolean indicating if this is a new instance
        update_fields: Set of field names being updated (None if all fields)
        **kwargs: Additional signal kwargs
    """
    
    # Skip if this is a newly created member (only process updates)
    if created:
        logger.info(f"[MEMBER SIGNAL] New Member created: {instance}, skipping email")
        return
    
    logger.info(f"[MEMBER SIGNAL] Member updated: {instance}, status={instance.approval_status}, update_fields={update_fields}")
    
    # Check if user_profile exists
    if not instance.user_profile:
        logger.warning(f"[MEMBER SIGNAL] Member {instance} has no user_profile, cannot send email")
        return
    
    user_email = instance.user_profile.email
    user_name = instance.user_profile.name
    
    # Only send emails for approved or rejected status
    if instance.approval_status == 'approved':
        logger.info(f"[MEMBER SIGNAL] Processing approval for {user_email}")
        template_name = 'emails/member_approval_email.html'
        subject = f'Welcome to {settings.SITE_NAME} - Membership Approved!'
        email_context = {
            'user_name': user_name,
            'site_name': getattr(settings, 'SITE_NAME', 'BSBCS'),
            'site_url': getattr(settings, 'SITE_URL', 'https://example.com'),
        }
        
    elif instance.approval_status == 'rejected':
        logger.info(f"[MEMBER SIGNAL] Processing rejection for {user_email}")
        template_name = 'emails/member_rejection_email.html'
        subject = f'{settings.SITE_NAME} - Membership Application Update'
        email_context = {
            'user_name': user_name,
            'rejection_reason': instance.rejection_reason or 'Not specified',
            'site_name': getattr(settings, 'SITE_NAME', 'BSBCS'),
            'support_email': getattr(settings, 'CONTACT_EMAIL', 'support@example.com'),
        }
    else:
        logger.info(f"[MEMBER SIGNAL] Member {instance} status is '{instance.approval_status}', no email to send")
        return
    
    # Send email
    try:
        logger.info(f"[MEMBER SIGNAL] Rendering template: {template_name}")
        html_message = render_to_string(template_name, email_context)
        plain_message = strip_tags(html_message)
        logger.info(f"[MEMBER SIGNAL] Template rendered successfully")
        
        logger.info(f"[MEMBER SIGNAL] Sending {instance.approval_status} email to {user_email}")
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"[MEMBER SIGNAL] Email sent successfully to {user_email}")
    except Exception as e:
        logger.error(f"[MEMBER SIGNAL] Failed to send email to {user_email}: {str(e)}", exc_info=True)
        # Print to console for debugging (no unicode to avoid cp1252 encoding issues on Windows)
        import traceback
        print("\n" + "="*60)
        print("!!! EMAIL SEND ERROR !!!")
        print("="*60)
        print(f"Error: {str(e)}")
        print(f"Template: {template_name}")
        print(f"Email: {user_email}")
        print("="*60)
        print(traceback.format_exc())
        print("="*60 + "\n")
