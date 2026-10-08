============
N1ED editors
============

Django apps to use the `N1ED <https://n1ed.com>`_ content builder in the admin.

- ``n1ed``: shared settings, the image upload view and the widgets' JavaScript.
  Required by the other two.
- ``n1edtinymce``: TinyMCE 8 + N1ED, both bundled.

  - ``n1edtinymce.widgets.N1EDTinyMCEWidget``

- ``n1edckeditor``: CKEditor 4 + N1ED.

  - ``n1edckeditor.widgets.N1EDCKEditor4Widget``: bundled CKEditor 4.22.1.
  - ``n1edckeditor.widgets.N1EDCKEditorWidget``: CKEditor from django-ckeditor.

Which widget?
-------------

==========================  =======================  =================  ======================
Widget                      Editor                   Security updates   Needs django-ckeditor
==========================  =======================  =================  ======================
``N1EDTinyMCEWidget``       TinyMCE 8 (bundled)      yes                no
``N1EDCKEditor4Widget``     CKEditor 4.22.1          no (end of life)   no
``N1EDCKEditorWidget``      django-ckeditor's        no (end of life)   yes
==========================  =======================  =================  ======================

Use ``N1EDTinyMCEWidget`` for new work. The CKEditor widgets edit exactly like
before, for projects that are not ready to switch. Both editors keep N1ED's
blocks (Bootstrap grid, ``data-*`` attributes, inline styles, icons, the
``widgets.js`` script) when content is opened and saved again.

N1ED's own code always loads from ``cloud.n1ed.com``; the editors and the N1ED
add-on files are served from your static files. If N1ED's cloud is unreachable
(network, an ad blocker), the editor starts after ~7 seconds without N1ED, and
the content is kept as is.

Install
-------

From a built package::

    python -m build --sdist                              # in this repo
    pip install dist/tracsa_utils-0.5.tar.gz             # in your project

Or with Poetry, in the project's ``pyproject.toml``::

    tracsa-utils = {path = "/path/to/tracsa-utils/dist/tracsa_utils-0.5.tar.gz"}

For ``N1EDCKEditorWidget`` install the extra: ``tracsa_utils[ckeditor]``.

Quick start
-----------

1. Add ``n1ed`` and the editor app(s) you use to ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'n1ed',
        'n1edtinymce',     # and/or 'n1edckeditor'
    ]

   Without ``n1ed``, ``manage.py check`` reports error ``n1ed.E001``.

2. Add your N1ED API key::

    N1ED_CKEDITOR_KEY = 'n1edApiKey'

3. Use the widget in your form::

    from n1edtinymce.widgets import N1EDTinyMCEWidget

    class PostForm(forms.ModelForm):
        class Meta:
            model = Post
            fields = '__all__'
            widgets = {
                'content': N1EDTinyMCEWidget(),
            }

4. In production, run ``python manage.py collectstatic``.

Images: Flmngr or your own storage
----------------------------------

Every widget can use either N1ED's file manager (Flmngr) or the upload view of
the ``n1ed`` app, which saves images in a Django storage.

**Flmngr** is used when ``N1ED_CKEDITOR_FLMNGR_CONFIG`` is set::

    N1ED_CKEDITOR_FLMNGR_CONFIG = {
        'accessKey': '...',
        'urlFileManager': 'https://files.flmngr.com/flmngr',
        'urlFiles': 'https://bucket.s3.us-east-1.amazonaws.com/',
    }

**Your own storage**: turn Flmngr off and include the upload view::

    # settings.py
    N1ED_USE_FLMNGR = False          # or leave N1ED_CKEDITOR_FLMNGR_CONFIG unset

    # urls.py
    urlpatterns = [
        ...
        path('n1ed/', include('n1ed.urls')),
    ]

With Flmngr off, its buttons (Upload, Browse, Edit image) are hidden, and the
editor's image dialog, paste and drop upload to the view. Only staff users can
upload, and the widgets send the CSRF token. Uploaded files get a random
suffix, so they never overwrite each other; with Pillow installed, files that
are not real images are rejected.

Flmngr can also be turned on/off per field::

    N1EDTinyMCEWidget(flmngr=False)
    N1EDTinyMCEWidget(flmngr=True)

Upload settings (all optional)::

    N1ED_UPLOAD_STORAGE = 'editor'          # alias in STORAGES or a storage class path;
                                            # default_storage when unset
    N1ED_UPLOAD_PATH = 'uploads/%Y/%m/'     # strftime pattern
    N1ED_UPLOAD_MAX_SIZE = 10 * 1024 * 1024
    N1ED_UPLOAD_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']

Example: images in S3 with `django-storages <https://django-storages.readthedocs.io>`_
(``pip install django-storages[s3]``), while the rest of the media stays where it
is. AWS credentials come from the usual ``AWS_ACCESS_KEY_ID`` and
``AWS_SECRET_ACCESS_KEY`` environment variables::

    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
        'editor': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'bucket_name': 'n1ed-tracsa',
                'region_name': 'us-east-1',
                'querystring_auth': False,   # public URLs, stored in the content
                'file_overwrite': False,
            },
        },
    }
    N1ED_UPLOAD_STORAGE = 'editor'

The bucket must serve the uploaded files publicly, as it does for Flmngr.

Limitations with Flmngr off: there is no browser for images uploaded before;
images are uploaded, not picked from a library.

Editor options
--------------

``N1EDTinyMCEWidget`` and ``N1EDCKEditor4Widget`` start from defaults that keep
N1ED content intact. Override them per project with named configs, or per
field with ``config``::

    N1ED_EDITOR_CONFIGS = {
        'blog': {
            'height': 700,
            # TinyMCE options: https://www.tiny.cloud/docs/tinymce/latest/
            'toolbar': 'undo redo | blocks | bold italic | link image | code',
        },
    }

    N1EDTinyMCEWidget(config_name='blog')
    N1EDTinyMCEWidget(config={'height': 300})

The options are passed to the editor as is, so use TinyMCE options for
``N1EDTinyMCEWidget`` and CKEditor 4 options for ``N1EDCKEditor4Widget``.
``N1EDCKEditorWidget`` keeps reading django-ckeditor's ``CKEDITOR_CONFIGS``
(``config_name=...``).

Trying it in a project
----------------------

The quickest way to test changes of this repo in a project (e.g. sitsa_api) is an
editable install, so there is nothing to rebuild::

    # Poetry, in the project's pyproject.toml
    tracsa-utils = {path = "/home/you/Tracsa/utils/tracsa-utils", develop = true}

    # or pip
    pip install -e /home/you/Tracsa/utils/tracsa-utils

Then:

1. Add ``'n1ed'`` (and ``'n1edtinymce'`` to try TinyMCE) to ``INSTALLED_APPS``
   and ``path('n1ed/', include('n1ed.urls'))`` to the URLs.
2. Switch one field to the widget you want to try, e.g. in ``blog/forms.py``::

    'content': N1EDTinyMCEWidget(flmngr=False),

   Fields using ``N1EDCKEditorWidget`` keep working, so you can compare both
   editors side by side.
3. Run ``python manage.py check`` and ``python manage.py runserver`` (with
   ``DEBUG = True`` static files are served without ``collectstatic``).
4. Open the field in the admin and check:

   - The N1ED toolbar and the purple "Block" button appear. If not, look at the
     browser console for ``Could not reach our server`` and at the Network tab
     for blocked requests to ``cloud.n1ed.com``.
   - Open an existing record and save it without changes: the content must be
     the same (compare it in the page or the database).
   - With ``flmngr=False``: Upload/Browse/Edit image are gone; insert an image
     with the image button (Upload tab) or paste/drop one, save, and check the
     file under ``MEDIA_ROOT/uploads/`` (or in the bucket with
     ``N1ED_UPLOAD_STORAGE``).
   - With ``flmngr=True``: Upload/Browse/Edit image open Flmngr.

Updating the bundled editors
----------------------------

Versions are pinned in ``scripts/update_vendor.py``; bump them and run::

    python scripts/update_vendor.py

Then run the browser tests (below), which check that the editors start, upload
images and keep N1ED content.

Licenses
--------

TinyMCE is GPL-2.0-or-later (the widget sets ``license_key: 'gpl'``), the N1ED
add-ons are GPL-3.0, and CKEditor 4.22.1 is GPL/LGPL/MPL. They are only served
to the admin's browser.

Upgrading from 0.4
------------------

- Add ``'n1ed'`` to ``INSTALLED_APPS`` (``n1ed.E001`` reminds you).
- ``from n1edckeditor.widgets import N1EDCKEditorWidget`` still works; install
  ``tracsa_utils[ckeditor]`` if the project does not depend on django-ckeditor
  itself.
- The N1ED plugin and skin moved to ``static/n1edckeditor/ckeditor4/``; run
  ``collectstatic`` on deploy.

=============
Preview Image
=============

1. Add ``tracsa_admin`` to ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'tracsa_admin',
    ]

2. Use the widget in your form::

    from tracsa_admin.widgets import ImagePreviewWidget

    class MyModelForm(ModelForm):
        class Meta:
            model = MyModel
            fields = '__all__'
            widgets = {
                'my_image_field': ImagePreviewWidget,
            }

=====
Tests
=====

::

    pip install -e ".[test]"
    pytest

Optional suites, skipped when their tools are missing:

- Browser tests (``tests/test_browser.py``): ``pip install playwright`` and
  ``playwright install chromium``. They start each widget in Chromium, upload
  an image and check that N1ED-style content survives a round trip.
  N1ED's cloud is blocked during these tests, so they do not need network.
- JavaScript regression test (``tests/test_fixups_js.py``):
  ``npm install --prefix tests/js``.
