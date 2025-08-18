from django.conf import settings

def google_api_key(request):
    """Context processor para hacer disponible GOOGLE_API_KEY en todos los templates"""
    return {
        'GOOGLE_API_KEY': getattr(settings, 'GOOGLE_API_KEY', None)
    } 