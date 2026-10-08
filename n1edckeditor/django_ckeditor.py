"""N1ED on top of django-ckeditor (pip install tracsa_utils[ckeditor]).

Import it from ``n1edckeditor.widgets``.
"""
from ckeditor.widgets import CKEditorWidget

from django.forms.widgets import Media
from django.templatetags.static import static

from n1ed import conf

from .options import N1ED_REMOVE_PLUGINS, upload_options

PLUGIN_NAME = 'N1ED-editor'


def _split_plugins(value):
    if not value:
        return []
    if isinstance(value, str):
        value = value.split(',')
    return [plugin.strip() for plugin in value if plugin.strip()]


class N1EDCKEditorWidget(CKEditorWidget):
    """
    flmngr: True/False to force Flmngr on/off; None follows N1ED_USE_FLMNGR.
    When Flmngr is off, images go to the ``n1ed:upload`` view.
    """

    def __init__(
        self,
        config_name='default',
        extra_plugins=None,
        remove_plugins=None,
        external_plugin_resources=None,
        flmngr=None,
        *args,
        **kwargs,
    ):
        super().__init__(
            config_name,
            extra_plugins,
            external_plugin_resources,
            *args,
            **kwargs,
        )
        self.flmngr = conf.use_flmngr(flmngr)

        extra = _split_plugins(self.config.get('extraPlugins'))
        if PLUGIN_NAME not in extra:
            extra.append(PLUGIN_NAME)
        self.config['extraPlugins'] = ','.join(extra)

        if not any(name == PLUGIN_NAME for name, *_ in self.external_plugin_resources):
            self.external_plugin_resources = list(self.external_plugin_resources) + [(
                PLUGIN_NAME,
                static(f'n1edckeditor/ckeditor4/plugins/{PLUGIN_NAME}/'),
                'plugin.js',
            )]

        api_key = self.config.pop('api_key', None)
        if api_key:
            self.config['apiKey'] = api_key

        remove = _split_plugins(self.config.get('removePlugins'))
        remove += _split_plugins(remove_plugins or self.config.pop('remove_plugins', None))
        for plugin in N1ED_REMOVE_PLUGINS:
            if plugin not in remove:
                remove.append(plugin)
        self.config['removePlugins'] = ','.join(dict.fromkeys(remove))

        self.config['allowedContent'] = True
        self.config.update(conf.n1ed_options(self.flmngr))

    def _set_config(self):
        # Reversing URLs has to wait until render time.
        if not self.flmngr:
            url = conf.upload_url()
            if url:
                for key, value in upload_options(url).items():
                    self.config.setdefault(key, value)
        super()._set_config()

    @property
    def media(self):
        # Listing ckeditor.js keeps the fixups after it when Django merges media.
        return super().media + Media(js=[
            'ckeditor/ckeditor/ckeditor.js',
            'n1edckeditor/fixups.js',
            'n1ed/csrf.js',
        ])
