"""TinyMCE 8 + N1ED, both bundled."""
from django.templatetags.static import static

from n1ed import conf
from n1ed.widgets import N1EDEditorWidget, language

STATIC = 'n1edtinymce/'

# Languages with a language pack in static/n1edtinymce/tinymce/langs.
LANGUAGES = ['es']


class N1EDTinyMCEWidget(N1EDEditorWidget):
    editor = 'tinymce'
    scripts = [STATIC + 'tinymce/tinymce.min.js']

    def default_config(self):
        config = {
            'base_url': static(STATIC + 'tinymce').rstrip('/'),
            'suffix': '.min',
            'license_key': 'gpl',
            'promotion': False,
            'branding': False,
            'height': 500,
            'menubar': 'edit view insert format table',
            'plugins': (
                'n1ed advlist anchor autolink charmap code fullscreen image link '
                'lists media preview searchreplace table visualblocks wordcount'
            ),
            # Keep the stored HTML as is: N1ED blocks rely on classes, data-*
            # attributes, inline styles and scripts, and URLs stay absolute.
            'valid_elements': '*[*]',
            'extended_valid_elements': 'script[*],style[*],i[*],span[*]',
            'valid_children': '+body[style|script],+div[style|script],+a[div|h1|h2|h3|h4|h5|h6|p|img|span]',
            'convert_urls': False,
            'entity_encoding': 'raw',
            'allow_script_urls': True,
            'sandbox_iframes': False,
            'convert_unsafe_embeds': False,
        }
        if language() in LANGUAGES:
            config['language'] = language()
        return config

    def upload_config(self, url):
        return {
            'images_upload_url': url,
            'automatic_uploads': True,
            'image_uploadtab': True,
            'images_file_types': ','.join(conf.upload_extensions()),
        }
