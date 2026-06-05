from .models import SiteSettings

def site_settings(request):
    """
    Context processor to make site settings available in all templates.
    """
    try:
        settings = SiteSettings.get_settings()
        return {'site_settings': settings}
    except Exception:
        # Return empty dict if settings don't exist yet
        return {'site_settings': None}
