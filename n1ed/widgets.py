import json

from django import forms
from django.templatetags.static import static
from django.utils.translation import get_language

from . import conf


def language():
    return (get_language() or 'en').lower().split('-')[0]


class N1EDEditorWidget(forms.Textarea):
    """Textarea started by n1ed/init.js with the editor in ``scripts``.

    Subclasses set ``editor`` and ``scripts`` and build the editor options.
    Takes ``config_name`` (a key of N1ED_EDITOR_CONFIGS), ``config`` (extra
    options for this widget) and ``flmngr`` (True/False to force Flmngr on/off;
    None follows N1ED_USE_FLMNGR). When Flmngr is off, images are uploaded to
    the ``n1ed:upload`` view if ``n1ed.urls`` is included.
    """
    editor = None
    scripts = []

    def __init__(self, config_name='default', config=None, flmngr=None, attrs=None):
        super().__init__(attrs)
        self.config_name = config_name
        self.extra_config = config or {}
        self.flmngr = flmngr

    class Media:
        js = ['n1ed/csrf.js', 'n1ed/init.js']

    def default_config(self):
        return {}

    def upload_config(self, url):
        return {}

    def build_config(self):
        flmngr = conf.use_flmngr(self.flmngr)
        config = self.default_config()
        config.update(conf.n1ed_options(flmngr))
        upload = None if flmngr else conf.upload_url()
        if upload:
            config.update(self.upload_config(upload))
        config.update(conf.editor_config(self.config_name))
        config.update(self.extra_config)
        return config, upload

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        config, upload = self.build_config()
        widget_attrs = context['widget']['attrs']
        widget_attrs.update({
            'data-n1ed-editor': self.editor,
            'data-n1ed-config': json.dumps(config),
            'data-n1ed-scripts': json.dumps([static(path) for path in self.scripts]),
        })
        if upload:
            widget_attrs['data-n1ed-upload'] = upload
        # The editor replaces the textarea; "required" would block submitting.
        widget_attrs.pop('required', None)
        return context
