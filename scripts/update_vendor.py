"""Download the editors and the N1ED add-ons into the apps' static folders.

    python scripts/update_vendor.py

Versions are pinned below; bump them and re-run to update.
"""
import io
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

CKEDITOR_VERSION = '4.22.1'
TINYMCE_VERSION = '8.9.3'
TINYMCE_I18N_VERSION = '26.9.28'

CKEDITOR_URL = (
    'https://download.cksource.com/CKEditor/CKEditor/'
    f'CKEditor%20{CKEDITOR_VERSION}/ckeditor_{CKEDITOR_VERSION}_full.zip'
)
TINYMCE_URL = f'https://registry.npmjs.org/tinymce/-/tinymce-{TINYMCE_VERSION}.tgz'
TINYMCE_I18N_URL = (
    f'https://registry.npmjs.org/tinymce-i18n/-/tinymce-i18n-{TINYMCE_I18N_VERSION}.tgz'
)
N1ED_CKEDITOR_URL = 'https://n1ed.com/download/n1ed-ckeditor.zip'
N1ED_TINYMCE_URL = 'https://n1ed.com/download/n1ed-tinymce.zip'

ROOT = Path(__file__).resolve().parent.parent
CKEDITOR_STATIC = ROOT / 'n1edckeditor' / 'static' / 'n1edckeditor'
TINYMCE_STATIC = ROOT / 'n1edtinymce' / 'static' / 'n1edtinymce'

CKEDITOR_LANGUAGES = ['en', 'es']
TINYMCE_LANGUAGES = ['es']  # English is built in
CKEDITOR_SKIP = {
    'samples', 'adapters', 'vendor', 'bender-runner.config.json',
    'build-config.js', 'CHANGES.md', 'README.md', 'SECURITY.md',
}

TINYMCE_PLUGINS = [
    'advlist', 'anchor', 'autolink', 'charmap', 'code', 'fullscreen', 'image',
    'link', 'lists', 'media', 'preview', 'searchreplace', 'table',
    'visualblocks', 'wordcount',
]


def download(url):
    print(f'downloading {url}')
    with urllib.request.urlopen(url) as response:
        return response.read()


def unzip(data, dest):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for member in archive.namelist():
            if member.startswith('/') or '..' in Path(member).parts:
                raise ValueError(f'unsafe path in archive: {member}')
        archive.extractall(dest)


def untar(data, dest):
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(dest, filter='data')


def copy(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


def vendor_ckeditor(tmp):
    unzip(download(CKEDITOR_URL), tmp / 'ckeditor')
    unzip(download(N1ED_CKEDITOR_URL), tmp / 'n1ed-ckeditor')
    src = tmp / 'ckeditor' / 'ckeditor'
    dest = CKEDITOR_STATIC / 'ckeditor4'
    shutil.rmtree(dest, ignore_errors=True)

    for path in src.iterdir():
        if path.name in CKEDITOR_SKIP:
            continue
        if path.name == 'lang':
            for lang in CKEDITOR_LANGUAGES:
                copy(path / f'{lang}.js', dest / 'lang' / f'{lang}.js')
            continue
        copy(path, dest / path.name)

    # Plugins with their own translations: keep only the languages we ship.
    for lang_dir in dest.glob('plugins/**/lang'):
        for lang_file in lang_dir.glob('*.js'):
            if lang_file.stem not in CKEDITOR_LANGUAGES:
                lang_file.unlink()

    n1ed = tmp / 'n1ed-ckeditor'
    copy(n1ed / 'plugins' / 'N1ED-editor', dest / 'plugins' / 'N1ED-editor')
    copy(n1ed / 'skins' / 'n1theme', dest / 'skins' / 'n1theme')
    copy(n1ed / 'LICENSE', dest / 'plugins' / 'N1ED-editor' / 'LICENSE')


def vendor_tinymce(tmp):
    untar(download(TINYMCE_URL), tmp / 'tinymce')
    unzip(download(N1ED_TINYMCE_URL), tmp / 'n1ed-tinymce')
    src = tmp / 'tinymce' / 'package'
    dest = TINYMCE_STATIC / 'tinymce'
    shutil.rmtree(dest, ignore_errors=True)

    for name in ['tinymce.min.js', 'license.md', 'notices.txt']:
        copy(src / name, dest / name)
    copy(src / 'themes' / 'silver' / 'theme.min.js', dest / 'themes' / 'silver' / 'theme.min.js')
    copy(src / 'models' / 'dom' / 'model.min.js', dest / 'models' / 'dom' / 'model.min.js')
    copy(src / 'icons' / 'default' / 'icons.min.js', dest / 'icons' / 'default' / 'icons.min.js')
    for skin in ['ui/oxide', 'ui/oxide-dark', 'content/default', 'content/dark']:
        for path in (src / 'skins' / skin).iterdir():
            if path.name.endswith('.min.css') or path.suffix == '.js':
                copy(path, dest / 'skins' / skin / path.name)
    for plugin in TINYMCE_PLUGINS:
        copy(src / 'plugins' / plugin / 'plugin.min.js', dest / 'plugins' / plugin / 'plugin.min.js')

    untar(download(TINYMCE_I18N_URL), tmp / 'tinymce-i18n')
    i18n = tmp / 'tinymce-i18n' / 'package'
    for lang in TINYMCE_LANGUAGES:
        copy(i18n / 'langs8' / f'{lang}.js', dest / 'langs' / f'{lang}.js')
    copy(i18n / 'LICENSE.md', dest / 'langs' / 'LICENSE.md')

    n1ed = tmp / 'n1ed-tinymce'
    copy(n1ed / 'plugins' / 'n1ed' / 'plugin.min.js', dest / 'plugins' / 'n1ed' / 'plugin.min.js')
    copy(n1ed / 'LICENSE', dest / 'plugins' / 'n1ed' / 'LICENSE')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        vendor_ckeditor(Path(tmp))
        vendor_tinymce(Path(tmp))
    print(f'CKEditor {CKEDITOR_VERSION} and TinyMCE {TINYMCE_VERSION} vendored')


if __name__ == '__main__':
    main()
