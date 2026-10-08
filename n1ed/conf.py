"""Settings shared by every N1ED widget.

N1ED_CKEDITOR_KEY             N1ED API key.
N1ED_CKEDITOR_FLMNGR_CONFIG   Flmngr options (accessKey, urlFileManager, urlFiles).
N1ED_USE_FLMNGR               Use Flmngr for images. Defaults to True when
                              N1ED_CKEDITOR_FLMNGR_CONFIG is set. When False, images
                              are uploaded through ``n1ed.urls`` instead.
N1ED_EDITOR_CONFIGS           {config_name: {...}} editor options merged into the
                              defaults of the N1EDEditorWidget subclasses.
N1ED_UPLOAD_STORAGE           Storage for uploads: an alias of STORAGES or a dotted
                              path to a storage class. Defaults to default_storage.
N1ED_UPLOAD_PATH              strftime pattern for the upload folder.
N1ED_UPLOAD_MAX_SIZE          Max upload size in bytes.
N1ED_UPLOAD_EXTENSIONS        Allowed image extensions.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse

FLMNGR_REQUIRED_KEYS = ['accessKey', 'urlFileManager', 'urlFiles']


def api_key():
    return getattr(settings, 'N1ED_CKEDITOR_KEY', '') or ''


def flmngr_config():
    config = getattr(settings, 'N1ED_CKEDITOR_FLMNGR_CONFIG', None)
    if not config:
        return None
    if not isinstance(config, dict):
        raise ImproperlyConfigured(
            'N1ED_CKEDITOR_FLMNGR_CONFIG must be a dictionary type.'
        )
    for key in FLMNGR_REQUIRED_KEYS:
        if key not in config:
            raise ImproperlyConfigured(f'No {key} found in your configuration')
    return config


def use_flmngr(override=None):
    if override is not None:
        return override
    return getattr(settings, 'N1ED_USE_FLMNGR', flmngr_config() is not None)


def editor_config(config_name):
    configs = getattr(settings, 'N1ED_EDITOR_CONFIGS', {})
    if config_name == 'default' and config_name not in configs:
        return {}
    if config_name not in configs:
        raise ImproperlyConfigured(
            f"No configuration named '{config_name}' found in N1ED_EDITOR_CONFIGS."
        )
    return dict(configs[config_name])


def upload_url():
    """URL of the upload view, or None when n1ed.urls is not included."""
    try:
        return reverse('n1ed:upload')
    except NoReverseMatch:
        return None


def upload_path():
    return getattr(settings, 'N1ED_UPLOAD_PATH', 'uploads/%Y/%m/')


def upload_max_size():
    return getattr(settings, 'N1ED_UPLOAD_MAX_SIZE', 10 * 1024 * 1024)


def upload_extensions():
    return getattr(
        settings, 'N1ED_UPLOAD_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    )


def n1ed_options(flmngr):
    """N1ED options turning Flmngr (and ImgPen, which saves through it) on or off."""
    options = {}
    key = api_key()
    if key:
        options['apiKey'] = key
    if flmngr:
        config = flmngr_config()
        if config:
            options['Flmngr'] = config
    else:
        options['enableFlmngr'] = False
        options['enableImgPen'] = False
        # N1ED keeps its Flmngr "Upload" and "Browse" buttons otherwise.
        hidden = {'isVisible': False, 'isVisible_v2': False}
        options['ui'] = {'toolbarButtons': {'Upload': hidden, 'Flmngr': hidden}}
    return options

