from .models import SiteSetting


def branding(request):
    try:
        setting = SiteSetting.current()
    except Exception:
        setting = None
    return {'brand': setting}
