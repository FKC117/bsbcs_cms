#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conference.settings')
django.setup()

from website.models import Member
from django.utils import timezone

# Get the pending member
pending = Member.objects.filter(approval_status='pending').first()

if pending:
    print(f"Found pending member: {pending.user_profile.name}")
    print(f"  ID: {pending.id}")
    print(f"  Status BEFORE: {pending.approval_status}")
    print(f"  Email: {pending.user_profile.email}")
    
    # Approve it
    print("\n[ACTION] Approving member...")
    pending.approval_status = 'approved'
    pending.approved_at = timezone.now()
    pending.save(update_fields=['approval_status', 'approved_at'])
    
    # Check in memory
    print(f"  Status in memory AFTER save: {pending.approval_status}")
    
    # Refresh from DB
    pending.refresh_from_db()
    print(f"  Status from DB AFTER refresh: {pending.approval_status}")
    
    # Query fresh from DB
    fresh = Member.objects.get(id=pending.id)
    print(f"  Status fresh query: {fresh.approval_status}")
    
    print("\n[SUCCESS] Member approved! Email should have been sent.")
else:
    print("No pending members found")
