from django.apps import apps
from django.core.checks import Error


def n1ed_installed(app_configs, **kwargs):
    """Registered by the editor apps, which use n1ed's settings, views and static files."""
    if apps.is_installed('n1ed'):
        return []
    return [Error(
        "'n1ed' must be in INSTALLED_APPS to use the N1ED editor apps.",
        hint="Add 'n1ed' to INSTALLED_APPS.",
        id='n1ed.E001',
    )]
