from django import template
from django.urls import reverse, NoReverseMatch
from django.core.cache import cache
import re

from website.models import SiteSettings, NavigationLink, HeroSection, CallToAction

register = template.Library()

# Cache timeout (in seconds): 1 hour
CACHE_TIMEOUT = 3600


@register.simple_tag
def get_site_settings():
    """Return the first SiteSettings instance or None.
    
    Results are cached for 1 hour to reduce database queries.
    """
    cached = cache.get('site_settings')
    if cached is not None:
        return cached
    
    settings = SiteSettings.objects.first()
    cache.set('site_settings', settings, CACHE_TIMEOUT)
    return settings


@register.simple_tag
def get_navigation_links():
    """Return a list of navigation link dicts: {'label':..., 'url':...}.

    This resolves URL names when possible and falls back to the stored value.
    Results are cached for 1 hour to reduce database queries.
    """
    cached = cache.get('navigation_links')
    if cached is not None:
        return cached
    
    navs = []
    for nav in NavigationLink.objects.filter(is_active=True).order_by('order'):
        url = nav.url_name or ''
        try:
            url = reverse(nav.url_name) if nav.url_name else ''
        except (NoReverseMatch, TypeError):
            url = nav.url_name
        navs.append({'label': nav.label, 'url': url})
    
    cache.set('navigation_links', navs, CACHE_TIMEOUT)
    return navs


@register.simple_tag
def get_hero_section(page_name):
    """Return the HeroSection instance for a specific page.
    
    Results are cached for 1 hour to reduce database queries.
    """
    cache_key = f'hero_section_{page_name}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    hero = HeroSection.objects.filter(page=page_name).first()
    cache.set(cache_key, hero, CACHE_TIMEOUT)
    return hero


@register.simple_tag
def get_call_to_action(page_name):
    """Return the CallToAction instance for a specific page.
    
    Results are cached for 1 hour to reduce database queries.
    """
    cache_key = f'call_to_action_{page_name}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    cta = CallToAction.objects.filter(page=page_name).first()
    cache.set(cache_key, cta, CACHE_TIMEOUT)
    return cta


@register.simple_tag(takes_context=True)
def get_call_to_action_current(context):
    """Return a CallToAction for the current request's view name (if any),
    otherwise fall back to the most recent CTA.

    This tag requires request to be available in the template context (Django
    provides it when you use RequestContext or render shortcuts which pass
    the request). Results are cached per view name for CACHE_TIMEOUT seconds.
    """
    request = context.get('request')
    view_name = None
    if request is not None:
        resolver = getattr(request, 'resolver_match', None)
        if resolver:
            view_name = resolver.url_name

    cache_key = f'call_to_action_current_{view_name or "__latest"}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    cta = None
    if view_name:
        cta = CallToAction.objects.filter(page=view_name).order_by('-id').first()

    # Do not fall back to the most-recent CTA for other pages.
    # If there is no CTA for the current view, return None so templates
    # can choose to render nothing when appropriate.

    cache.set(cache_key, cta, CACHE_TIMEOUT)
    return cta


@register.filter
def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats."""
    if not url:
        return None
    
    url = url.strip()
    
    # Handle youtu.be format
    match = re.search(r'youtu\.be/([^?&\s]+)', url)
    if match:
        return match.group(1)
    
    # Handle youtube.com/watch?v= format
    match = re.search(r'youtube\.com/watch\?.*v=([^&\s]+)', url)
    if match:
        return match.group(1)
    
    # Handle youtube.com/embed/ format
    match = re.search(r'youtube\.com/embed/([^?&\s]+)', url)
    if match:
        return match.group(1)
    
    # Handle youtube.com/v/ format (old)
    match = re.search(r'youtube\.com/v/([^?&\s]+)', url)
    if match:
        return match.group(1)
    
    # Handle full embed URLs (youtube.com/embed/{id})
    match = re.search(r'(?:youtube\.com/)?embed/([^?&\s]+)', url)
    if match:
        return match.group(1)
    
    # Handle direct video ID (11 chars, alphanumeric with - and _)
    match = re.search(r'^([a-zA-Z0-9_-]{11})$', url)
    if match:
        return match.group(1)
    
    return None


@register.filter
def youtube_thumbnail(url):
    """Extract YouTube video ID and return thumbnail URL."""
    video_id = extract_youtube_id(url)
    if video_id:
        # Use medium quality thumbnail (320x180)
        return f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
    return None
