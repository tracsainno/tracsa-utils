from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template import RequestContext, Template

from n1edckeditor.widgets import N1EDCKEditor4Widget, N1EDCKEditorWidget
from n1edtinymce.widgets import N1EDTinyMCEWidget

WIDGETS = {
    'django-ckeditor': N1EDCKEditorWidget,
    'ckeditor4': N1EDCKEditor4Widget,
    'tinymce': N1EDTinyMCEWidget,
}

PAGE = Template(
    '<!doctype html><html><head>{{ form.media }}</head><body>'
    '<form method="post">{% csrf_token %}{{ form.as_p }}<button>Save</button></form>'
    '<pre id="saved">{{ saved }}</pre></body></html>'
)


@staff_member_required
def editor(request, kind):
    class Form(forms.Form):
        body = forms.CharField(widget=WIDGETS[kind]())

    form = Form(request.POST or None)
    saved = form.cleaned_data['body'] if form.is_valid() else ''
    return HttpResponse(PAGE.render(RequestContext(request, {'form': form, 'saved': saved})))
