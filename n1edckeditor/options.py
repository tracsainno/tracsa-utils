# N1ED has better support for these, and exportpdf needs a token URL
# (it logs "exportpdf-no-token-url" on every editor otherwise).
N1ED_REMOVE_PLUGINS = ['iframe', 'magicline', 'exportpdf']


def upload_options(url):
    """CKEditor 4 options to upload images (dialog and paste/drop) to ``url``."""
    return {
        'filebrowserUploadUrl': url,
        'filebrowserImageUploadUrl': url,
        'filebrowserUploadMethod': 'xhr',
        'uploadUrl': url,
        'imageUploadUrl': url,
        # uploadimage handles pasted/dropped images instead of the clipboard plugin.
        'clipboard_handleImages': False,
    }
