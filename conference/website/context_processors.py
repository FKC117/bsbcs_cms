from django.urls import reverse, NoReverseMatch
from .models import SiteSettings, NavigationLink


def site_settings(request):
    settings = SiteSettings.objects.first()

    # Build navigation links with resolved URLs when possible
    navigation_links = []
    for nav in NavigationLink.objects.filter(is_active=True).order_by('order'):
        url = nav.url_name or ''
        try:
            # Try to reverse as a Django URL name
            url = reverse(nav.url_name)
        except (NoReverseMatch, TypeError):
            # If reversing fails, assume the field contains a direct URL or path
            url = nav.url_name
        navigation_links.append({'label': nav.label, 'url': url})

    return {
        'site_settings': settings,
        'navigation_links': navigation_links,
    }
