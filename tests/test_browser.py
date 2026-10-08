"""End-to-end checks in Chromium (pip install playwright && playwright install chromium).

N1ED's cloud is blocked so the run is deterministic: this covers our part
(vendored editors, init.js, CSRF and the upload view), not N1ED itself.
"""
import base64
import io
import os
import re

import pytest
from PIL import Image

playwright = pytest.importorskip('playwright.sync_api')

KINDS = ['django-ckeditor', 'ckeditor4', 'tinymce']

READY = """() => (window.CKEDITOR && Object.values(CKEDITOR.instances).some(e => e.status === 'ready'))
    || (window.tinymce && tinymce.activeEditor && tinymce.activeEditor.initialized)"""

SET_AND_GET = """async (html) => {
    if (window.CKEDITOR) {
        const ed = Object.values(CKEDITOR.instances)[0];
        await new Promise(resolve => ed.setData(html, resolve));
        return ed.getData();
    }
    tinymce.activeEditor.setContent(html);
    return tinymce.activeEditor.getContent();
}"""

UPLOAD = """async (png) => {
    const blob = await (await fetch('data:image/png;base64,' + png)).blob();
    if (window.CKEDITOR) {
        const ed = Object.values(CKEDITOR.instances)[0];
        const loader = ed.uploadRepository.create(blob, 'photo.png');
        const url = await new Promise((resolve, reject) => {
            loader.on('uploaded', () => resolve(loader.url));
            loader.on('error', () => reject(new Error(loader.message)));
            loader.loadAndUpload(ed.config.uploadUrl);
        });
        await new Promise(resolve => ed.setData('<p><img src="' + url + '"></p>', resolve));
        return url;
    }
    const ed = tinymce.activeEditor;
    const info = ed.editorUpload.blobCache.create('photo', blob, png);
    ed.editorUpload.blobCache.add(info);
    ed.setContent('<p><img src="' + info.blobUri() + '"></p>');
    const [result] = await ed.uploadImages();
    if (!result.status) throw new Error('upload failed');
    return result.element.getAttribute('src');
}"""

# Markup N1ED blocks rely on: Bootstrap grid, data-* attributes, inline styles,
# icons and the widgets script.
CONTENT = (
    '<div class="container-fluid" data-bootstrap-contains="container">'
    '<div class="container"><div class="row gx-3" data-n1ed-block-category="text">'
    '<div class="col-12 col-lg-6" style="padding: 10px;">'
    '<h2 style="text-align: center;">Title</h2>'
    '<p>Text <a class="btnSitsa btnPrimary" href="https://example.com/x">link</a></p>'
    '<i data-fa-icon="star" data-fa-style="solid"></i>'
    '<img class="img-fluid" data-n1ed-img-width="100" src="https://example.com/a.png">'
    '</div></div></div></div>'
    '<script src="https://cdn.n1ed.com/widgets.js" data-ts="1"></script>'
)


def facts(html):
    return sorted(
        re.findall(r'class="[^"]*"|data-[\w-]+="[^"]*"|src="[^"]*"|href="[^"]*"', html)
        + [text.strip() for text in re.findall(r'(?<=>)[^<>]+(?=<)', html) if text.strip()]
    )


def png():
    data = io.BytesIO()
    Image.new('RGB', (4, 4), 'red').save(data, 'PNG')
    return base64.b64encode(data.getvalue()).decode()


@pytest.fixture(scope='module')
def browser():
    os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')
    with playwright.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:
            pytest.skip(f'Chromium is not installed: {e}')
        yield browser
        browser.close()


@pytest.fixture
def page(browser, live_server, django_user_model, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    django_user_model.objects.create_user('staff', password='pass', is_staff=True)
    context = browser.new_context()
    context.route(re.compile(r'https://cloud\.n1ed\.com/.*'), lambda route: route.abort())
    context.add_init_script('window.N1ED_FAILSAFE_TIMEOUT = 300')
    page = context.new_page()
    errors = []
    # Ignore the failures caused by blocking N1ED's cloud.
    page.on('pageerror', lambda e: 'n1ed.com' not in str(e) and errors.append(str(e)))
    page.goto(live_server.url + '/admin/login/')
    page.fill('#id_username', 'staff')
    page.fill('#id_password', 'pass')
    page.click('input[type=submit]')
    yield page, errors
    context.close()


def open_editor(page, live_server, kind):
    page.goto(f'{live_server.url}/editor/{kind}/')
    page.wait_for_function(READY, timeout=20000)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('kind', KINDS)
def test_content_round_trip(page, live_server, kind):
    page, errors = page
    open_editor(page, live_server, kind)

    html = page.evaluate(SET_AND_GET, CONTENT)

    assert facts(html) == facts(CONTENT)
    assert errors == []


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('kind', KINDS)
def test_upload_and_save(page, live_server, tmp_path, kind):
    page, errors = page
    open_editor(page, live_server, kind)

    url = page.evaluate(UPLOAD, png())
    with page.expect_navigation():
        page.click('button:text("Save")')

    assert url.startswith('/media/uploads/')
    assert (tmp_path / url[len('/media/'):]).exists()
    assert url in page.inner_text('#saved')
    assert errors == []
