from django.forms.widgets import FileInput
from django.template.loader import get_template


class ImagePreviewWidget(FileInput):

    def render(self, name, value, attrs=None, renderer=None):

        return get_template('image_preview_widget.html').render({
                'field_name': name,
                'src': value if value else None,
            })
