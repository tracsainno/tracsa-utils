from tracsa_admin.widgets import ImagePreviewWidget


class FakeFile:
    url = '/media/photo.png'

    def __str__(self):
        return 'photo.png'


def test_renders_empty_input():
    html = ImagePreviewWidget().render('photo', None)

    assert 'name="photo"' in html
    assert 'id="id_photo"' in html
    assert 'Currently' not in html
    assert 'display:none' in html


def test_renders_current_image():
    html = ImagePreviewWidget().render('photo', FakeFile())

    assert 'Currently' in html
    assert 'href="/media/photo.png"' in html
    assert 'src="/media/photo.png"' in html
    assert 'display:none' not in html
