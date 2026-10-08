import json
import re

import pytest
from django.core.exceptions import ImproperlyConfigured

from n1edckeditor.widgets import N1EDCKEditorWidget


def rendered_config(widget):
    html = widget.render('body', '<p>hi</p>')
    match = re.search(r'data-config="([^"]*)"', html)
    return json.loads(match.group(1).replace('&quot;', '"'))


def test_enables_n1ed_plugin():
    widget = N1EDCKEditorWidget()

    assert widget.config['extraPlugins'] == 'N1ED-editor'
    assert widget.external_plugin_resources == [
        ('N1ED-editor', '/static/n1edckeditor/ckeditor4/plugins/N1ED-editor/', 'plugin.js'),
    ]


def test_keeps_extra_plugins_from_settings(settings):
    settings.CKEDITOR_CONFIGS = {'default': {'extraPlugins': 'codesnippet,widget'}}

    widget = N1EDCKEditorWidget()

    assert widget.config['extraPlugins'] == 'codesnippet,widget,N1ED-editor'


def test_removes_plugins_n1ed_replaces():
    widget = N1EDCKEditorWidget()

    assert widget.config['removePlugins'] == 'iframe,magicline,exportpdf'


def test_merges_remove_plugins_from_settings_and_argument(settings):
    settings.CKEDITOR_CONFIGS = {'default': {'removePlugins': 'elementspath'}}

    widget = N1EDCKEditorWidget(remove_plugins='scayt,iframe')

    assert widget.config['removePlugins'] == (
        'elementspath,scayt,iframe,magicline,exportpdf'
    )


def test_api_key_from_settings(settings):
    settings.N1ED_CKEDITOR_KEY = 'MYKEY'

    assert N1EDCKEditorWidget().config['apiKey'] == 'MYKEY'


def test_api_key_from_ckeditor_config(settings):
    settings.CKEDITOR_CONFIGS = {'default': {'api_key': 'CONFKEY'}}

    widget = N1EDCKEditorWidget()

    assert widget.config['apiKey'] == 'CONFKEY'
    assert 'api_key' not in widget.config


def test_no_api_key_by_default():
    assert 'apiKey' not in N1EDCKEditorWidget().config


def test_config_is_rendered(settings):
    settings.N1ED_CKEDITOR_KEY = 'MYKEY'

    config = rendered_config(N1EDCKEditorWidget())

    assert config['apiKey'] == 'MYKEY'
    assert config['extraPlugins'] == 'N1ED-editor'
    assert config['allowedContent'] is True
    assert config['versionCheck'] is False


def test_media_loads_fixups_after_ckeditor():
    js = [str(path) for path in N1EDCKEditorWidget().media._js]

    assert js.index('n1edckeditor/fixups.js') > js.index('ckeditor/ckeditor/ckeditor.js')


def test_media_loads_csrf_hook_after_ckeditor():
    js = [str(path) for path in N1EDCKEditorWidget().media._js]

    assert js.index('n1ed/csrf.js') > js.index('ckeditor/ckeditor/ckeditor.js')


FLMNGR = {
    'accessKey': 'key',
    'urlFileManager': '/flmngr/',
    'urlFiles': '/media/',
}


def test_flmngr_on_when_configured(settings):
    settings.N1ED_CKEDITOR_FLMNGR_CONFIG = FLMNGR

    config = rendered_config(N1EDCKEditorWidget())

    assert config['Flmngr'] == FLMNGR
    assert 'enableFlmngr' not in config
    assert 'filebrowserUploadUrl' not in config


def test_flmngr_off_uses_own_upload():
    config = rendered_config(N1EDCKEditorWidget())

    assert config['enableFlmngr'] is False
    assert config['enableImgPen'] is False
    assert 'Flmngr' not in config
    assert config['filebrowserUploadUrl'] == '/n1ed/upload/'
    assert config['uploadUrl'] == '/n1ed/upload/'
    assert config['filebrowserUploadMethod'] == 'xhr'


def test_flmngr_off_by_setting(settings):
    settings.N1ED_CKEDITOR_FLMNGR_CONFIG = FLMNGR
    settings.N1ED_USE_FLMNGR = False

    config = rendered_config(N1EDCKEditorWidget())

    assert config['enableFlmngr'] is False
    assert 'Flmngr' not in config


def test_flmngr_off_by_widget_argument(settings):
    settings.N1ED_CKEDITOR_FLMNGR_CONFIG = FLMNGR

    config = rendered_config(N1EDCKEditorWidget(flmngr=False))

    assert config['enableFlmngr'] is False
    assert config['filebrowserUploadUrl'] == '/n1ed/upload/'


def test_no_upload_url_without_n1ed_urls(settings):
    settings.ROOT_URLCONF = 'tests.urls_without_n1ed'

    config = rendered_config(N1EDCKEditorWidget())

    assert config['enableFlmngr'] is False
    assert 'filebrowserUploadUrl' not in config


@pytest.mark.parametrize('missing', ['accessKey', 'urlFileManager', 'urlFiles'])
def test_flmngr_config_requires_keys(settings, missing):
    settings.N1ED_CKEDITOR_FLMNGR_CONFIG = {
        k: v for k, v in FLMNGR.items() if k != missing
    }

    with pytest.raises(ImproperlyConfigured, match=missing):
        N1EDCKEditorWidget()


def test_flmngr_config_must_be_dict(settings):
    settings.N1ED_CKEDITOR_FLMNGR_CONFIG = ['accessKey']

    with pytest.raises(ImproperlyConfigured, match='dictionary'):
        N1EDCKEditorWidget()
