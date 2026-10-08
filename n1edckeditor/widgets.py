"""CKEditor 4 + N1ED.

    N1EDCKEditor4Widget   bundled CKEditor 4.22.1 (no django-ckeditor needed)
    N1EDCKEditorWidget    CKEditor from django-ckeditor (pip install tracsa_utils[ckeditor])
"""
from django.templatetags.static import static

from n1ed.widgets import N1EDEditorWidget, language

from .options import N1ED_REMOVE_PLUGINS, upload_options

STATIC = 'n1edckeditor/'


class N1EDCKEditor4Widget(N1EDEditorWidget):
    editor = 'ckeditor4'
    scripts = [
        STATIC + 'ckeditor4/ckeditor.js',
        STATIC + 'fixups.js',
        'n1ed/csrf.js',
    ]

    def default_config(self):
        return {
            'extraPlugins': 'N1ED-editor',
            'removePlugins': ','.join(N1ED_REMOVE_PLUGINS),
            'skin': 'n1theme',
            'allowedContent': True,
            'versionCheck': False,
            'language': language(),
            'height': 400,
            'width': '100%',
        }

    def upload_config(self, url):
        return upload_options(url)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['data-n1ed-basepath'] = static(STATIC + 'ckeditor4/')
        return context


def __getattr__(name):
    # Imported on demand so the bundled widget works without django-ckeditor.
    if name == 'N1EDCKEditorWidget':
        from .django_ckeditor import N1EDCKEditorWidget
        return N1EDCKEditorWidget
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
