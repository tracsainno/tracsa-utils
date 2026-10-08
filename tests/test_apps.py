import subprocess
import sys

from django.core import checks

from n1ed.checks import n1ed_installed


def test_check_passes_with_n1ed_installed():
    assert n1ed_installed(None) == []


def test_check_fails_without_n1ed(settings):
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'n1ed']

    errors = checks.run_checks()

    assert [e.id for e in errors if e.id.startswith('n1ed')] == ['n1ed.E001']


def test_bundled_ckeditor_widget_does_not_import_django_ckeditor():
    # A fresh interpreter, since this test session already imported ckeditor.
    code = (
        'import sys, django\n'
        'from django.conf import settings\n'
        'settings.configure()\n'
        'from n1edckeditor.widgets import N1EDCKEditor4Widget\n'
        'from n1edtinymce.widgets import N1EDTinyMCEWidget\n'
        'assert "ckeditor" not in sys.modules, "django-ckeditor was imported"\n'
    )
    subprocess.run([sys.executable, '-c', code], check=True)


def test_django_ckeditor_widget_keeps_its_import_path():
    from n1edckeditor.django_ckeditor import N1EDCKEditorWidget as widget
    from n1edckeditor.widgets import N1EDCKEditorWidget

    assert N1EDCKEditorWidget is widget
