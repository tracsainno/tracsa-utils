import os
import uuid

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage, storages
from django.http import JsonResponse
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.text import get_valid_filename, slugify
from django.views.decorators.http import require_POST

from . import conf


def get_storage():
    name = getattr(settings, 'N1ED_UPLOAD_STORAGE', None)
    if not name:
        return default_storage
    if '.' not in name:
        return storages[name]
    return import_string(name)()


def error(message, status=400):
    return JsonResponse(
        {'uploaded': 0, 'error': {'message': message}}, status=status,
    )


def is_image(upload):
    try:
        from PIL import Image
    except ImportError:
        return True
    try:
        with Image.open(upload) as image:
            image.verify()
    except Exception:
        return False
    finally:
        upload.seek(0)
    return True


def upload_name(filename):
    stem, ext = os.path.splitext(filename)
    stem = slugify(stem)[:80] or 'image'
    name = get_valid_filename(f'{stem}-{uuid.uuid4().hex[:8]}{ext.lower()}')
    return timezone.now().strftime(conf.upload_path()) + name


@staff_member_required
@require_POST
def upload(request):
    """Image upload for CKEditor 4 (field "upload") and TinyMCE (field "file").

    The response carries the keys both editors read: "url" for CKEditor and
    "location" for TinyMCE.
    """
    upload = request.FILES.get('upload') or request.FILES.get('file')
    if upload is None:
        return error('No file was sent.')

    ext = os.path.splitext(upload.name)[1].lower().lstrip('.')
    if ext not in conf.upload_extensions():
        return error(f'File type .{ext} is not allowed.')
    if upload.size > conf.upload_max_size():
        return error('The file is too large.')
    if not is_image(upload):
        return error('The file is not a valid image.')

    storage = get_storage()
    name = storage.save(upload_name(upload.name), upload)
    url = storage.url(name)
    return JsonResponse({
        'uploaded': 1,
        'fileName': os.path.basename(name),
        'url': url,
        'location': url,
    })
