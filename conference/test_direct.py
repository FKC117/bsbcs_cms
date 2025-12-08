#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conference.settings')
django.setup()

from website.models import Member
from django.utils import timezone
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check members
members = Member.objects.all()
print(f"\nTotal members in DB: {members.count()}")

for m in members[:5]:
    print(f"  ID: {m.id}, Name: {m.user_profile.name if m.user_profile else 'No Profile'}, Status: {m.approval_status}")

# Try to update one
if members.exists():
    member = members.first()
    print(f"\nTesting approval of: {member}")
    print(f"Before: status={member.approval_status}, approved_at={member.approved_at}")
    
    # Update
    member.approval_status = 'approved'
    member.approved_at = timezone.now()
    print("Calling save()...")
    member.save(update_fields=['approval_status', 'approved_at'])
    
    # Refresh from DB
    member.refresh_from_db()
    print(f"After:  status={member.approval_status}, approved_at={member.approved_at}")
