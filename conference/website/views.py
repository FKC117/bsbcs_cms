from django.shortcuts import render
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from pathlib import Path
import os
from django.http import FileResponse, Http404
from django.conf import settings
import re
from django.core.paginator import Paginator
from .models import (
    HeroSection, CarouselItem, NewsTickerItem, QuickAccessCard, StatisticCounter,
    MemberSpotlight, ResearchHighlight, Event, CallToAction, BoardMember,
    Committee, Partnership, Award, AnnualReport, ResourceCategory, ResourceItem,
    Webinar, Member, NavigationLink, OrganizationalValue, TimelineSection
)
from .models import ResearchInterestArea, Speciality
from .forms import MembershipForm


def favicon(request):
    favicon_path = os.path.join(settings.BASE_DIR, 'website', 'static', 'img', 'favicon.ico')
    try:
        return FileResponse(open(favicon_path, 'rb'))
    except FileNotFoundError:
        # Return a proper 404 if favicon is missing instead of raising an unhandled exception
        raise Http404("favicon not found")


def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats."""
    if not url:
        return None
    
    # Handle youtu.be format
    match = re.search(r'youtu\.be/([^?&]+)', url)
    if match:
        return match.group(1)
    
    # Handle youtube.com format
    match = re.search(r'youtube\.com/watch\?v=([^&]+)', url)
    if match:
        return match.group(1)
    
    # Handle youtube.com/embed format
    match = re.search(r'youtube\.com/embed/([^?&]+)', url)
    if match:
        return match.group(1)
    
    return None

def homepage(request):
    hero = HeroSection.objects.filter(page='homepage').first()
    carousel_items = CarouselItem.objects.filter(hero_section=hero) if hero else []
    news_tickers = NewsTickerItem.objects.filter(is_active=True).order_by('order')
    quick_access_cards = QuickAccessCard.objects.filter(page='homepage').order_by('order')
    stats_counters = StatisticCounter.objects.filter(page='homepage').order_by('order')
    member_spotlights = MemberSpotlight.objects.filter(is_featured=True).order_by('order')
    # Only show highlights flagged for homepage (highlight=True)
    research_highlights = ResearchHighlight.objects.filter(highlight=True).order_by('order')
    # Prefer registration app's Event model for upcoming events display on homepage
    try:
        from registration.models import Event as RegEvent
    except Exception:
        RegEvent = Event  # fallback to local Event model

    # Query only upcoming events from the registration app and order by start_date
    try:
        events = RegEvent.objects.filter(event_status='upcoming').order_by('start_date')
    except Exception:
        # Fallback to the existing local events list if RegEvent doesn't support these fields
        events = Event.objects.all().order_by('order', 'date')
    # Use the latest CallToAction entry for homepage (most recent).
    # We keep the model's order field available but prefer the latest DB entry
    # so content managers can update the hero CTA by creating a new entry.
    call_to_action = CallToAction.objects.filter(page='homepage').order_by('-id').first()
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')

    context = {
        'hero': hero,
        'carousel_items': carousel_items,
        'news_tickers': news_tickers,
        'quick_access_cards': quick_access_cards,
        'stats_counters': stats_counters,
        'member_spotlights': member_spotlights,
        'research_highlights': research_highlights,
        'events': events,
        'call_to_action': call_to_action,
        'navigation_links': navigation_links,
    }
    return render(request, 'pages/homepage.html', context)


def about(request):
    hero = HeroSection.objects.filter(page='about').first()
    stats_counters = StatisticCounter.objects.filter(page='about').order_by('order')
    board_members = BoardMember.objects.all().order_by('order')
    committees = Committee.objects.all().order_by('order')
    partnerships = Partnership.objects.all().order_by('order')
    awards = Award.objects.all().order_by('order', '-year')
    call_to_action = CallToAction.objects.filter(page='about').first()
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')
    
    # Fetch timeline section with ordered items
    timeline_section = TimelineSection.objects.order_by('order').first()
    timeline_items = []
    if timeline_section:
        timeline_items = list(timeline_section.items.all())  # type: ignore
    
    # Fetch organizational values grouped by type
    mission = OrganizationalValue.objects.filter(value_type='mission').first()
    vision = OrganizationalValue.objects.filter(value_type='vision').first()
    values = OrganizationalValue.objects.filter(value_type='value').order_by('order')

    # Prepare values_items for the template. If there are multiple `value` rows,
    # use each row's title as an item. If there is a single `value` row which
    # contains a multi-line description (e.g. authors pasted a list into the
    # description field), split it into list items for rendering.
    import re
    values_items = []
    if values.count() > 1:
        for v in values:
            # prefer the title for short list items, fallback to description
            text = v.title or (v.description or '').strip()
            if text:
                values_items.append(text)
    elif values.count() == 1:
        single = values.first()
        desc = (single.description or '').strip()  # type: ignore
        if desc:
            # split on newlines first
            parts = [p.strip() for p in re.split(r'[\r\n]+', desc) if p.strip()]
            if len(parts) == 1:
                # if still single, try splitting on common separators
                parts = [p.strip() for p in re.split(r'[;\u2022,]+', desc) if p.strip()]
            values_items = parts
        else:
            # no description, use the title as a single item
            if single.title:  # type: ignore
                values_items = [single.title]  # type: ignore
    
    # Determine a header title and icon for the Values card.
    # Prefer an explicit "Values" meta row when present (title like 'Values' or 'Our Values').
    values_header_title = 'Values'
    values_header_icon_url = None
    if values.exists():
        # try to find a meta/header row
        header = values.filter(title__iregex=r'^(values|our values?)$').first()
        if header:
            values_header_title = header.title  # type: ignore
            if header.icon_svg:  # type: ignore
                values_header_icon_url = header.icon_svg.url  # type: ignore
        else:
            # no explicit header row: if there's a single row, use its title/icon as header
            if values.count() == 1:
                single = values.first()
                values_header_title = single.title or values_header_title  # type: ignore
                if single.icon_svg:  # type: ignore
                    values_header_icon_url = single.icon_svg.url  # type: ignore
            else:
                # multiple rows and no header candidate: leave generic title and no icon
                values_header_title = 'Values'

    context = {
        'hero': hero,
        'stats_counters': stats_counters,
        'board_members': board_members,
        'committees': committees,
        'partnerships': partnerships,
        'awards': awards,
        'call_to_action': call_to_action,
        'navigation_links': navigation_links,
        'mission': mission,
        'vision': vision,
        'values': values,
        'values_items': values_items,
        'values_header_title': values_header_title,
        'values_header_icon_url': values_header_icon_url,
        'timeline_section': timeline_section,
        'timeline_items': timeline_items,
    }
    return render(request, 'pages/about_site.html', context)


def knowledge_center(request):
    hero = HeroSection.objects.filter(page='knowledge_center').first()
    resource_categories = ResourceCategory.objects.all().order_by('order')
    # Featured Resources section: only featured items
    featured_resources = ResourceItem.objects.filter(is_featured=True).order_by('order')
    # Clinical Guidelines section: all items (regardless of is_featured)
    all_resources = ResourceItem.objects.all().order_by('order')
    webinars = Webinar.objects.all().order_by('order')
    call_to_action = CallToAction.objects.filter(page='knowledge_center').first()
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')

    context = {
        'hero': hero,
        'resource_categories': resource_categories,
        'featured_resources': featured_resources,
        'all_resources': all_resources,
        'webinars': webinars,
        'call_to_action': call_to_action,
        'navigation_links': navigation_links,
    }
    return render(request, 'pages/knowledge_center.html', context)


def member_directory(request):
    hero = HeroSection.objects.filter(page='member_directory').first()
    # Only show members with 'approved' status in the directory
    members = Member.objects.filter(approval_status='approved').order_by('order')
    # Fetch specialties and research interest areas for the advanced filter dropdowns
    specialities = Speciality.objects.all().order_by('name')
    research_areas = ResearchInterestArea.objects.all().order_by('name')
    call_to_action = CallToAction.objects.filter(page='member_directory').first()
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')

    context = {
        'hero': hero,
        'members': members,
        'specialities': specialities,
        'research_areas': research_areas,
        'call_to_action': call_to_action,
        'navigation_links': navigation_links,
    }
    return render(request, 'pages/member_directory.html', context)


def events(request):
    # Render the legacy registration index at /events/
    # Use the registration app's Event model (has fields like start_date, end_date, event_status)
    try:
        from registration.models import Event as RegEvent, UserProfile as RegUserProfile
    except Exception:
        RegEvent = Event  # fallback to local Event model
        RegUserProfile = None

    user_profile = None
    if request.user.is_authenticated and RegUserProfile:
        try:
            user_profile = RegUserProfile.objects.get(user=request.user)
        except RegUserProfile.DoesNotExist:  # type: ignore[name-defined]
            user_profile = None

    hero = HeroSection.objects.filter(page='events').first()
    news_tickers = NewsTickerItem.objects.filter(is_active=True).order_by('order')

    # Mirror registration.index view behavior: group events by status
    active_events = RegEvent.objects.filter(event_status='active').order_by('-start_date')
    upcoming_events = RegEvent.objects.filter(event_status='upcoming').order_by('start_date')
    closed_events = RegEvent.objects.filter(event_status='closed').order_by('-end_date')

    call_to_action = CallToAction.objects.filter(page='events').first()
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')

    context = {
        'user_profile': user_profile,
        'hero': hero,
        'news_tickers': news_tickers,
        'active_events': active_events,
        'upcoming_events': upcoming_events,
        'closed_events': closed_events,
        'call_to_action': call_to_action,
        'navigation_links': navigation_links,
    }
    # Render the shared index template so /events/ behaves like the old index page
    return render(request, 'index.html', context)


def research_and_publications(request):
    hero = HeroSection.objects.filter(page='research_and_publications').first()
    stats_counters = StatisticCounter.objects.filter(page='research_and_publications').order_by('order')
    # Only include research highlights that are explicitly flagged as highlighted
    research_highlights = ResearchHighlight.objects.filter(highlight=True).order_by('order')
    # Also provide a full list of research highlights (regardless of the `highlight` flag)
    research_highlights_all = ResearchHighlight.objects.all().order_by('order')
    annual_reports = AnnualReport.objects.all().order_by('-year')
    call_to_action = CallToAction.objects.filter(page='research_and_publications').first()
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')

    context = {
        'hero': hero,
        'stats_counters': stats_counters,
        'research_highlights': research_highlights,
        'research_highlights_all': research_highlights_all,
        'annual_reports': annual_reports,
        'call_to_action': call_to_action,
        'navigation_links': navigation_links,
    }
    return render(request, 'pages/research_and_publications.html', context)

def webinars(request):
    hero = HeroSection.objects.filter(page='webinars').first()
    resource_categories = ResourceCategory.objects.all().order_by('order')
    resources = ResourceItem.objects.all().order_by('order')
    
    # Pagination settings: 6 items per page for each section
    items_per_page = 6
    
    # Get webinars and paginate
    webinars_all = Webinar.objects.filter(type='webinar').order_by('order')
    webinars_paginator = Paginator(webinars_all, items_per_page)
    webinars_page = request.GET.get('webinars_page', 1)
    try:
        webinars = webinars_paginator.page(webinars_page)
    except:
        webinars = webinars_paginator.page(1)
    
    # Get preceptorship webinars and paginate
    preceptorship_all = Webinar.objects.filter(type='perceptorship').order_by('order')
    preceptorship_paginator = Paginator(preceptorship_all, items_per_page)
    preceptorship_page = request.GET.get('preceptorship_page', 1)
    try:
        preceptorship_webinars = preceptorship_paginator.page(preceptorship_page)
    except:
        preceptorship_webinars = preceptorship_paginator.page(1)
    
    # Get GCI webinars and paginate
    gci_all = Webinar.objects.filter(type='gci').order_by('order')
    gci_paginator = Paginator(gci_all, items_per_page)
    gci_page = request.GET.get('gci_page', 1)
    try:
        gci_webinars = gci_paginator.page(gci_page)
    except:
        gci_webinars = gci_paginator.page(1)
    
    call_to_action = CallToAction.objects.filter(page='webinars').first()
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')

    context = {
        'hero': hero,
        'resource_categories': resource_categories,
        'resources': resources,
        'webinars': webinars,
        'preceptorship_webinars': preceptorship_webinars,
        'gci_webinars': gci_webinars,
        'call_to_action': call_to_action,
        'navigation_links': navigation_links,
    }
    return render(request, 'pages/webinars.html', context)


def webinar_detail(request, pk):
    """Display full webinar details including video and panelists."""
    webinar = Webinar.objects.get(pk=pk)
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')
    
    context = {
        'webinar': webinar,
        'navigation_links': navigation_links,
    }
    return render(request, 'pages/webinar_detail.html', context)


def sitemap_table(request):
    """Render a human-friendly, tabular sitemap page.

    Collects entries from the existing sitemap classes in
    `registration.sitemaps` and builds a list of rows with the
    following columns: URL, Title, Last modified, Changefreq, Priority.
    """
    from registration.sitemaps import (
        EventSitemap,
        StaticViewSitemap,
        PublicationSitemap,
        WebsiteStaticSitemap,
        WebinarSitemap,
    )

    sitemap_instances = [
        WebsiteStaticSitemap(),
        EventSitemap(),
        WebinarSitemap(),
        PublicationSitemap(),
        StaticViewSitemap(),
    ]

    rows = []

    # Friendly titles for well-known static names
    static_title_map = {
        'website:homepage': 'Home',
        'website:about': 'About',
        'website:member_directory': 'Members',
        'website:research_and_publications': 'Research & Publications',
        'website:knowledge_center': 'Resources',
        'website:events': 'Events',
        'website:webinars': 'Webinars',
    }

    for sm in sitemap_instances:
        changefreq = getattr(sm, 'changefreq', '')
        priority = getattr(sm, 'priority', '')
        try:
            items = list(sm.items())
        except Exception:
            items = []

        for item in items:
            # location may raise, guard it
            try:
                loc = sm.location(item)
            except Exception:
                # fallback: try str()
                try:
                    loc = str(item)
                except Exception:
                    loc = ''

            # lastmod if provided
            lastmod = None
            if hasattr(sm, 'lastmod'):
                try:
                    lastmod = sm.lastmod(item)
                except Exception:
                    lastmod = None

            # Determine a human-friendly title
            title = None
            # If the sitemap item is a named URL (string)
            if isinstance(item, str):
                title = static_title_map.get(item, item.replace('website:', '').replace('_', ' ').title())
            # If tuple used by StaticViewSitemap (('about', event_id))
            elif isinstance(item, (list, tuple)):
                try:
                    url_name = item[0]
                    arg = item[1] if len(item) > 1 else ''
                    title = f"{url_name.replace('_', ' ').title()} (Event {arg})"
                except Exception:
                    title = str(item)
            else:
                # Model instances: try common fields
                title = getattr(item, 'title', None) or getattr(item, 'name', None) or getattr(item, 'get_short_name', None)
                if callable(title):
                    try:
                        title = title()
                    except Exception:
                        title = None
                if not title:
                    try:
                        title = str(item)
                    except Exception:
                        title = ''

            rows.append({
                'loc': loc,
                'title': title,
                'lastmod': lastmod,
                'changefreq': changefreq,
                'priority': priority,
            })

    context = {
        'rows': rows,
    }
    return render(request, 'pages/sitemap_table.html', context)


def membership_form(request):
    """View for membership form submission and creation.
    
    Requires:
    1. User must be logged in (redirects to login if not)
    2. User must have a UserProfile (redirects to create_profile if not)
    3. Once both requirements are met, display membership form
    """
    from django.shortcuts import redirect
    from django.urls import reverse
    from registration.models import UserProfile
    
    # Check if user is logged in
    if not request.user.is_authenticated:
        # Redirect to login with next parameter pointing back to membership form
        return redirect(f'{reverse("login")}?next={reverse("website:membership_form")}')
    
    # Check if user has a UserProfile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Redirect to create_profile with next parameter pointing back to membership form
        return redirect(f'{reverse("create_profile")}?next={reverse("website:membership_form")}')
    
    if request.method == 'POST':
        form = MembershipForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            # Link Member to the user's UserProfile
            member.user_profile = user_profile
            # Set approval_status to pending (will be reviewed by admin)
            member.approval_status = 'pending'
            # Set order to a default high value (can be ordered later in admin)
            member.order = Member.objects.count() + 1
            member.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Render success message
            return render(request, 'pages/membership_success.html', {
                'member': member,
            })
    else:
        form = MembershipForm()
    
    hero = HeroSection.objects.filter(page='member_directory').first()
    call_to_action = CallToAction.objects.filter(page='member_directory').first()
    navigation_links = NavigationLink.objects.filter(is_active=True).order_by('order')
    
    context = {
        'form': form,
        'hero': hero,
        'call_to_action': call_to_action,
        'navigation_links': navigation_links,
        'user_profile': user_profile,
    }
    return render(request, 'pages/membership_form.html', context)