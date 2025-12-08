from django.contrib import admin
from .models import (
    SiteSettings,
    HeroSection, CarouselItem, NewsTickerItem, QuickAccessCard, StatisticCounter,
    MemberSpotlight, ResearchHighlight, Event, CallToAction, BoardMember,
    Committee, Partnership, Award, AnnualReport, ResourceCategory, ResourceItem,
    Webinar, Member, NavigationLink, OrganizationalValue, ResearchInterestArea, Speciality, Panelist
)
from .models import TimelineSection, TimelineItem

# HeroSection and related CarouselItems
@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('page', 'title')
    search_fields = ('title', 'page')


@admin.register(CarouselItem)
class CarouselItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'hero_section', 'order')
    list_filter = ('hero_section',)
    ordering = ('order',)
    search_fields = ('title',)


@admin.register(NewsTickerItem)
class NewsTickerItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'order', 'is_active')
    ordering = ('order',)
    search_fields = ('text',)


@admin.register(QuickAccessCard)
class QuickAccessCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'order')
    list_filter = ('page',)
    ordering = ('order',)
    search_fields = ('title',)


@admin.register(StatisticCounter)
class StatisticCounterAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'count_text', 'order')
    list_filter = ('page',)
    ordering = ('order',)
    search_fields = ('title',)

@admin.register(ResearchInterestArea)
class ResearchInterestAreaAdmin(admin.ModelAdmin):
    list_display = ('id','name')
@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(MemberSpotlight)
class MemberSpotlightAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'is_featured', 'order')
    list_filter = ('is_featured',)
    ordering = ('order',)
    search_fields = ('name', 'title')


@admin.register(ResearchHighlight)
class ResearchHighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'order')
    ordering = ('order',)
    search_fields = ('title',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'date', 'order')
    list_filter = ('event_type', 'date')
    ordering = ('order', 'date')
    search_fields = ('title',)


@admin.register(Panelist)
class PanelistAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(CallToAction)
class CallToActionAdmin(admin.ModelAdmin):
    list_display = ('title', 'page')
    list_filter = ('page',)
    search_fields = ('title',)


@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'title', 'order')
    list_filter = ('role',)
    ordering = ('order',)
    search_fields = ('name', 'title')


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_count', 'order')
    ordering = ('order',)
    search_fields = ('name',)


@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)
    search_fields = ('name',)


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'issuer', 'year', 'order')
    ordering = ('order', '-year')
    search_fields = ('title', 'issuer')


@admin.register(AnnualReport)
class AnnualReportAdmin(admin.ModelAdmin):
    list_display = ('year', 'order')
    ordering = ('-year',)
    search_fields = ('year',)


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)
    search_fields = ('name',)


@admin.register(ResourceItem)
class ResourceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'category', 'order')
    list_filter = ('resource_type', 'category')
    ordering = ('order',)
    search_fields = ('title',)


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'presenter_name', 'recorded_date', 'order')
    list_filter = ('type',)
    filter_horizontal = ('international_panel', 'national_panel', 'moderators')
    ordering = ('order',)
    search_fields = ('title', 'presenter_name')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('get_member_name', 'get_user_email', 'approval_status', 'approved_at', 'created_at', 'order')
    list_filter = ('approval_status', 'created_at', 'specialties', 'research_interest_areas')
    readonly_fields = ('created_at', 'updated_at', 'approved_at', 'rejected_at')
    ordering = ('-created_at',)
    search_fields = ('user_profile__name', 'user_profile__email', 'institution', 'position')
    actions = ['approve_members', 'reject_members']
    
    fieldsets = (
        ('User Profile', {
            'fields': ('user_profile', 'institution', 'position')
        }),
        ('Membership Details', {
            'fields': ('specialties', 'research_interest_areas', 'profile_description', 'image')
        }),
        ('Approval Status', {
            'fields': ('approval_status', 'rejection_reason', 'approved_at', 'rejected_at')
        }),
        ('Metadata', {
            'fields': ('order', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_member_name(self, obj):
        return obj.user_profile.name
    get_member_name.short_description = 'Name'

    def get_user_email(self, obj):
        return obj.user_profile.email
    get_user_email.short_description = 'Email'

    def approve_members(self, request, queryset):
        from django.utils import timezone
        from django.contrib import messages
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get pending members and iterate to trigger signals
        pending_members = queryset.filter(approval_status='pending')
        count = 0
        
        for member in pending_members:
            logger.info(f"[ADMIN ACTION] Approving member: {member.user_profile.name}")
            member.approval_status = 'approved'
            member.approved_at = timezone.now()
            member.save(update_fields=['approval_status', 'approved_at'])
            logger.info(f"[ADMIN ACTION] Member saved, checking new status: {member.approval_status}")
            count += 1
        
        self.message_user(request, f'{count} member(s) approved and notification emails sent.')
    approve_members.short_description = 'Approve selected members'

    def reject_members(self, request, queryset):
        from django.utils import timezone
        from django.contrib import messages
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get pending members and iterate to trigger signals
        pending_members = queryset.filter(approval_status='pending')
        count = 0
        
        for member in pending_members:
            # Check if rejection_reason is filled
            if not member.rejection_reason:
                logger.warning(f"[ADMIN ACTION] Member {member.user_profile.name} has no rejection reason")
                self.message_user(
                    request,
                    f'Member {member.user_profile.name} has no rejection reason. Please edit individually to add one.',
                    messages.WARNING
                )
                continue
            
            logger.info(f"[ADMIN ACTION] Rejecting member: {member.user_profile.name}")
            member.approval_status = 'rejected'
            member.rejected_at = timezone.now()
            member.save(update_fields=['approval_status', 'rejected_at'])
            logger.info(f"[ADMIN ACTION] Member saved, checking new status: {member.approval_status}")
            count += 1
        
        self.message_user(request, f'{count} member(s) rejected and notification emails sent.')
    reject_members.short_description = 'Reject selected members'

    def get_specialties(self, obj):
        return ', '.join([s.name for s in obj.specialties.all()])
    get_specialties.short_description = 'Specialties'

    def get_research_interests(self, obj):
        return ', '.join([r.name for r in obj.research_interest_areas.all()])
    get_research_interests.short_description = 'Research Interests'



# Tag model intentionally left unregistered (removed from Member). If you want to manage
# tags separately, re-register here.


@admin.register(NavigationLink)
class NavigationLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'url_name', 'order', 'is_active')
    ordering = ('order',)
    search_fields = ('label', 'url_name')


@admin.register(OrganizationalValue)
class OrganizationalValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'value_type', 'order')
    list_filter = ('value_type',)
    ordering = ('value_type', 'order')
    search_fields = ('title', 'description')


class TimelineItemInline(admin.TabularInline):
    model = TimelineItem
    extra = 1
    fields = ('event_date', 'title', 'description', 'order')


@admin.register(TimelineSection)
class TimelineSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order',)
    inlines = [TimelineItemInline]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'abbreviation')
    search_fields = ('site_name', 'abbreviation')

    def has_add_permission(self, request):
        # Allow only one SiteSettings instance via admin to keep it singleton-like
        from .models import SiteSettings as SS
        return not SS.objects.exists()