import html
import json
import re

import pytest
from django import forms
from django.core.exceptions import ImproperlyConfigured

from n1edckeditor.widgets import N1EDCKEditor4Widget
from n1edtinymce.widgets import N1EDTinyMCEWidget

FLMNGR = {
    'accessKey': 'key',
    'urlFileManager': '/flmngr/',
    'urlFiles': '/media/',
}

WIDGETS = [N1EDCKEditor4Widget, N1EDTinyMCEWidget]


def rendered_attrs(widget, value='<p>hi</p>'):
    output = widget.render('body', value, attrs={'id': 'id_body'})
    return {k: html.unescape(v) for k, v in re.findall(r'([\w-]+)="([^"]*)"', output)}


def rendered_config(widget):
    return json.loads(rendered_attrs(widget)['data-n1ed-config'])


@pytest.mark.parametrize('widget, editor', [
    (N1EDCKEditor4Widget, 'ckeditor4'),
    (N1EDTinyMCEWidget, 'tinymce'),
])
def test_renders_textarea_for_init_js(widget, editor):
    attrs = rendered_attrs(widget())

    assert attrs['data-n1ed-editor'] == editor
    assert json.loads(attrs['data-n1ed-scripts']) == [
        f'/static/{path}' for path in widget.scripts
    ]


@pytest.mark.parametrize('widget', WIDGETS)
def test_keeps_value_unescaped_once(widget):
    output = widget().render('body', '<p class="row">hi</p>')

    assert '&lt;p class=&quot;row&quot;&gt;hi&lt;/p&gt;' in output


@pytest.mark.parametrize('widget', WIDGETS)
def test_media_has_no_django_ckeditor(widget):
    js = [str(path) for path in widget().media._js]

    assert js == ['n1ed/csrf.js', 'n1ed/init.js']


@pytest.mark.parametrize('widget', WIDGETS)
def test_required_attribute_is_dropped(widget):
    class Form(forms.Form):
        body = forms.CharField(widget=widget())

    assert 'required' not in str(Form()['body'])


def test_ckeditor4_defaults(settings):
    settings.LANGUAGE_CODE = 'es-mx'
    attrs = rendered_attrs(N1EDCKEditor4Widget())
    config = json.loads(attrs['data-n1ed-config'])

    assert attrs['data-n1ed-basepath'] == '/static/n1edckeditor/ckeditor4/'
    assert config['extraPlugins'] == 'N1ED-editor'
    assert config['removePlugins'] == 'iframe,magicline,exportpdf'
    assert config['skin'] == 'n1theme'
    assert config['allowedContent'] is True
    assert config['versionCheck'] is False
    assert config['language'] == 'es'


def test_tinymce_defaults():
    config = rendered_config(N1EDTinyMCEWidget())

    assert config['base_url'] == '/static/n1edtinymce/tinymce'
    assert config['license_key'] == 'gpl'
    assert 'n1ed' in config['plugins'].split()
    assert config['valid_elements'] == '*[*]'
    assert config['convert_urls'] is False


@pytest.mark.parametrize('widget', WIDGETS)
def test_api_key(settings, widget):
    settings.N1ED_CKEDITOR_KEY = 'MYKEY'

    assert rendered_config(widget())['apiKey'] == 'MYKEY'


@pytest.mark.parametrize('widget', WIDGETS)
def test_flmngr_on_when_configured(settings, widget):
    settings.N1ED_CKEDITOR_FLMNGR_CONFIG = FLMNGR

    attrs = rendered_attrs(widget())
    config = json.loads(attrs['data-n1ed-config'])

    assert config['Flmngr'] == FLMNGR
    assert 'enableFlmngr' not in config
    assert 'data-n1ed-upload' not in attrs


@pytest.mark.parametrize('widget', WIDGETS)
def test_flmngr_off_uses_own_upload(widget):
    attrs = rendered_attrs(widget())
    config = json.loads(attrs['data-n1ed-config'])

    assert config['enableFlmngr'] is False
    assert config['enableImgPen'] is False
    assert attrs['data-n1ed-upload'] == '/n1ed/upload/'


@pytest.mark.parametrize('widget', WIDGETS)
def test_flmngr_off_by_setting(settings, widget):
    settings.N1ED_CKEDITOR_FLMNGR_CONFIG = FLMNGR
    settings.N1ED_USE_FLMNGR = False

    assert rendered_config(widget())['enableFlmngr'] is False


@pytest.mark.parametrize('widget', WIDGETS)
def test_flmngr_off_by_widget_argument(settings, widget):
    settings.N1ED_CKEDITOR_FLMNGR_CONFIG = FLMNGR

    assert rendered_config(widget(flmngr=False))['enableFlmngr'] is False


@pytest.mark.parametrize('widget', WIDGETS)
def test_flmngr_on_by_widget_argument_without_config(widget):
    config = rendered_config(widget(flmngr=True))

    assert 'enableFlmngr' not in config


def test_ckeditor4_upload_config():
    config = rendered_config(N1EDCKEditor4Widget())

    assert config['filebrowserUploadUrl'] == '/n1ed/upload/'
    assert config['imageUploadUrl'] == '/n1ed/upload/'
    assert config['filebrowserUploadMethod'] == 'xhr'


def test_tinymce_upload_config():
    config = rendered_config(N1EDTinyMCEWidget())

    assert config['images_upload_url'] == '/n1ed/upload/'
    assert config['image_uploadtab'] is True


@pytest.mark.parametrize('widget', WIDGETS)
def test_no_upload_without_n1ed_urls(settings, widget):
    settings.ROOT_URLCONF = 'tests.urls_without_n1ed'

    assert 'data-n1ed-upload' not in rendered_attrs(widget())


@pytest.mark.parametrize('widget', WIDGETS)
def test_named_config_and_widget_config(settings, widget):
    settings.N1ED_EDITOR_CONFIGS = {'blog': {'height': 900, 'menubar': False}}

    config = rendered_config(widget(config_name='blog', config={'height': 300}))

    assert config['menubar'] is False
    assert config['height'] == 300


@pytest.mark.parametrize('widget', WIDGETS)
def test_unknown_config_name(widget):
    with pytest.raises(ImproperlyConfigured, match='blog'):
        widget(config_name='blog').render('body', '')


@pytest.mark.parametrize('language, expected', [('es-mx', 'es'), ('en-us', None)])
def test_tinymce_language(settings, language, expected):
    settings.LANGUAGE_CODE = language

    assert rendered_config(N1EDTinyMCEWidget()).get('language') == expected


@pytest.mark.parametrize('widget', WIDGETS)
def test_flmngr_off_hides_its_toolbar_buttons(widget):
    buttons = rendered_config(widget())['ui']['toolbarButtons']

    assert buttons['Upload'] == {'isVisible': False, 'isVisible_v2': False}
    assert buttons['Flmngr'] == {'isVisible': False, 'isVisible_v2': False}
