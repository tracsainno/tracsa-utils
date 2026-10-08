import io
import re

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from PIL import Image

URL = '/n1ed/upload/'


def png(name='Foto Banner.png', size=(4, 4)):
    data = io.BytesIO()
    Image.new('RGB', size, 'red').save(data, 'PNG')
    return SimpleUploadedFile(name, data.getvalue(), content_type='image/png')


@pytest.fixture(autouse=True)
def media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
    return tmp_path


@pytest.fixture
def staff(django_user_model):
    return django_user_model.objects.create_user('staff', password='x', is_staff=True)


@pytest.fixture
def client(staff):
    client = Client()
    client.force_login(staff)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize('field', ['upload', 'file'])
def test_upload_image(client, media, field):
    response = client.post(URL, {field: png()})

    assert response.status_code == 200
    data = response.json()
    assert data['uploaded'] == 1
    assert data['url'] == data['location']
    assert data['url'].startswith('/media/uploads/')
    assert data['fileName'].startswith('foto-banner-')
    assert data['fileName'].endswith('.png')
    assert (media / data['url'][len('/media/'):]).exists()


@pytest.mark.django_db
def test_same_name_does_not_overwrite(client):
    first = client.post(URL, {'upload': png()}).json()['url']
    second = client.post(URL, {'upload': png()}).json()['url']

    assert first != second


@pytest.mark.django_db
def test_upload_path_setting(client, settings):
    settings.N1ED_UPLOAD_PATH = 'editor/%Y/'

    url = client.post(URL, {'upload': png()}).json()['url']

    assert re.match(r'^/media/editor/\d{4}/foto-banner-', url)


@pytest.mark.django_db
def test_storage_alias(client, settings, tmp_path):
    other = tmp_path / 'other'
    settings.STORAGES = {
        **settings.STORAGES,
        'editor': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {'location': other, 'base_url': 'https://cdn.example.com/'},
        },
    }
    settings.N1ED_UPLOAD_STORAGE = 'editor'

    url = client.post(URL, {'upload': png()}).json()['url']

    assert url.startswith('https://cdn.example.com/uploads/')
    assert any(other.rglob('*.png'))


@pytest.mark.django_db
def test_storage_class_path(client, settings):
    settings.N1ED_UPLOAD_STORAGE = 'django.core.files.storage.FileSystemStorage'

    assert client.post(URL, {'upload': png()}).status_code == 200


@pytest.mark.django_db
def test_rejects_extension(client):
    svg = SimpleUploadedFile('x.svg', b'<svg onload="alert(1)"/>', content_type='image/svg+xml')

    response = client.post(URL, {'upload': svg})

    assert response.status_code == 400
    assert response.json() == {'uploaded': 0, 'error': {'message': 'File type .svg is not allowed.'}}


@pytest.mark.django_db
def test_rejects_fake_image(client):
    fake = SimpleUploadedFile('x.png', b'not an image', content_type='image/png')

    response = client.post(URL, {'upload': fake})

    assert response.status_code == 400
    assert 'not a valid image' in response.json()['error']['message']


@pytest.mark.django_db
def test_rejects_large_file(client, settings):
    settings.N1ED_UPLOAD_MAX_SIZE = 10

    response = client.post(URL, {'upload': png()})

    assert response.status_code == 400
    assert 'too large' in response.json()['error']['message']


@pytest.mark.django_db
def test_requires_file(client):
    assert client.post(URL).status_code == 400


@pytest.mark.django_db
def test_requires_post(client):
    assert client.get(URL).status_code == 405


@pytest.mark.django_db
def test_requires_staff(django_user_model):
    client = Client()
    client.force_login(django_user_model.objects.create_user('user', password='x'))

    response = client.post(URL, {'upload': png()})

    assert response.status_code == 302


@pytest.mark.django_db
def test_anonymous_is_redirected():
    assert Client().post(URL, {'upload': png()}).status_code == 302


@pytest.mark.django_db
def test_requires_csrf_token(staff):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)

    assert client.post(URL, {'upload': png()}).status_code == 403

    client.get('/admin/')  # renders the logout form, which sets the CSRF cookie
    token = client.cookies['csrftoken'].value
    response = client.post(URL, {'upload': png()}, HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 200
