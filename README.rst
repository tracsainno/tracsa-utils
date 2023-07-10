=====
N1ED CKEditor
=====

This is a Django app to use N1ED pro plugin for ckeditor.

Quick start
-----------

1. Add "n1edckeditor" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        'n1edckeditor',
    ]


2. Add your key to settings like this:

    N1ED_CKEDITOR_KEY = 'n1edApiKey'

3. Run collect static in order to use plugin files.

   ``python manage.py collectstatic``

4. Use widget in your form:
    from n1edckeditor.widgets import N1EDCKEditorWidget

    ```
    class MyModelForm(ModelForm):
        class Meta:
            model = MyModel
            fields = '__all__'
            widgets = {
                'my_n1ed_field': N1EDCKEditorWidget()
            }
    ```
