import pytest
from django.contrib.staticfiles import finders

from n1edckeditor.widgets import N1EDCKEditor4Widget
from n1edtinymce.widgets import N1EDTinyMCEWidget


@pytest.mark.parametrize('path', [
    'n1edckeditor/fixups.js',
    'n1ed/csrf.js',
    'n1ed/init.js',
    'n1edckeditor/ckeditor4/ckeditor.js',
    'n1edckeditor/ckeditor4/lang/es.js',
    'n1edckeditor/ckeditor4/plugins/N1ED-editor/plugin.js',
    'n1edckeditor/ckeditor4/skins/n1theme/skin.js',
    'n1edckeditor/ckeditor4/skins/n1theme/editor.css',
    'n1edtinymce/tinymce/tinymce.min.js',
    'n1edtinymce/tinymce/plugins/n1ed/plugin.min.js',
    'n1edtinymce/tinymce/langs/es.js',
    'n1edtinymce/tinymce/themes/silver/theme.min.js',
    'n1edtinymce/tinymce/models/dom/model.min.js',
    'n1edtinymce/tinymce/icons/default/icons.min.js',
    'n1edtinymce/tinymce/skins/ui/oxide/skin.min.css',
    'n1edtinymce/tinymce/skins/content/default/content.min.css',
])
def test_static_files_are_found(path):
    assert finders.find(path)


def test_tinymce_plugins_are_vendored():
    plugins = N1EDTinyMCEWidget().default_config()['plugins'].split()

    for plugin in plugins:
        assert finders.find(f'n1edtinymce/tinymce/plugins/{plugin}/plugin.min.js'), plugin


@pytest.mark.parametrize('widget', [N1EDCKEditor4Widget, N1EDTinyMCEWidget])
def test_widget_scripts_are_vendored(widget):
    for path in widget.scripts:
        assert finders.find(path), path
