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
    list_display = ('name', 'get_specialties', 'get_research_interests', 'location', 'order')
    list_filter = ('specialties', 'research_interest_areas')
    ordering = ('order',)
    search_fields = ('name', 'specialties__name', 'research_interest_areas__name', 'location')

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