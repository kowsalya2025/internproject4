# app/context_processors.py
from django.conf import settings

def social_auth_context(request):
    return {
        'google_auth_enabled': bool(getattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')),
        'microsoft_auth_enabled': bool(getattr(settings, 'SOCIAL_AUTH_MICROSOFT_GRAPH_KEY', '')),
        'github_auth_enabled': bool(getattr(settings, 'SOCIAL_AUTH_GITHUB_KEY', '')),
    }