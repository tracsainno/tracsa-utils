import json
import shutil
import subprocess
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders

JS_DIR = Path(__file__).parent / 'js'

pytestmark = pytest.mark.skipif(
    not shutil.which('node') or not (JS_DIR / 'node_modules' / 'jsdom').exists(),
    reason='needs node and `npm install` in tests/js',
)


def test_bookmark_with_stale_offset_does_not_crash():
    result = subprocess.run(
        [
            'node', 'bookmark_fix.js',
            finders.find('ckeditor/ckeditor/ckeditor.js'),
            finders.find('n1edckeditor/fixups.js'),
        ],
        cwd=JS_DIR, capture_output=True, text=True, check=True,
    )
    output = json.loads(result.stdout)

    # The unpatched CKEditor reproduces the error seen after editing an image.
    assert output['before'] == {'error': "Cannot read properties of null (reading 'type')"}
    assert output['after']['bookmark']['collapsed'] is True
