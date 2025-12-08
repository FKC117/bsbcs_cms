"""
Management command to test member approval workflow end-to-end.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from website.models import Member
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test member approval workflow - approve a pending member and check if email is sent'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=== Testing Member Approval Workflow ==="))
        
        # Find a pending member
        pending_members = Member.objects.filter(approval_status='pending')
        
        if not pending_members.exists():
            self.stdout.write(self.style.ERROR("No pending members found!"))
            return
        
        member = pending_members.first()
        self.stdout.write(self.style.WARNING(f"\nFound pending member: {member}"))
        self.stdout.write(f"  Email: {member.user_profile.email}")
        self.stdout.write(f"  Current status: {member.approval_status}")
        
        self.stdout.write(self.style.WARNING("\n[STEP 1] Changing status to approved..."))
        member.approval_status = 'approved'
        member.approved_at = timezone.now()
        
        self.stdout.write(f"  Status before save: {member.approval_status}")
        member.save(update_fields=['approval_status', 'approved_at'])
        self.stdout.write(f"  Status after save: {member.approval_status}")
        
        # Reload from DB to verify
        member.refresh_from_db()
        self.stdout.write(f"  Status after refresh: {member.approval_status}")
        
        if member.approval_status == 'approved':
            self.stdout.write(self.style.SUCCESS("✓ Status changed successfully!"))
            self.stdout.write(self.style.SUCCESS("✓ Email should have been sent (check Django logs)"))
        else:
            self.stdout.write(self.style.ERROR("✗ Status did not change!"))
