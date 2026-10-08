from django.apps import AppConfig
from django.core import checks


class N1EDCKEditorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'n1edckeditor'

    def ready(self):
        from n1ed.checks import n1ed_installed
        checks.register(n1ed_installed)
