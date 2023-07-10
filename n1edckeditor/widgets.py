from ckeditor.widgets import CKEditorWidget

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class N1EDCKEditorWidget(CKEditorWidget):
    def __init__(
        self,
        config_name='default',
        extra_plugins=['N1ED-editor'],
        remove_plugins='iframe',
        external_plugin_resources=[(
            'N1ED-editor',
            '/static/plugins/N1ED-editor/',
            'plugin.js',
        )],
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
        api_key = getattr(settings, 'N1ED_CKEDITOR_KEY', '')

        api_key = api_key or self.config.pop('api_key', None) or ''
        if api_key:
            self.config['apiKey'] = api_key

        remove_plugins = remove_plugins or self.config.pop(
            'remove_plugins', None) or ''
        if remove_plugins:
            self.config['removePlugins'] = remove_plugins

        self.config['allowedContent'] = True

        n1ed_flmngr_conf = getattr(settings, 'N1ED_CKEDITOR_FLMNGR_CONFIG', None)

        if n1ed_flmngr_conf:
            if isinstance(n1ed_flmngr_conf, dict):
                if 'accessKey' in n1ed_flmngr_conf:
                    pass
                else:
                    raise ImproperlyConfigured('No accessKey found in your configuration')
                if 'urlFileManager' in n1ed_flmngr_conf:
                    pass
                else:
                    raise ImproperlyConfigured('No urlFileManager found in your configuration')
                if 'urlFiles' in n1ed_flmngr_conf:
                    pass
                else:
                    raise ImproperlyConfigured('No urlFiles found in your configuration')
                self.config['Flmngr'] = n1ed_flmngr_conf
            else:
                raise ImproperlyConfigured(
                    'N1ED_CKEDITOR_FLMNGR_CONFIG must be a dictionary type.'
                )
