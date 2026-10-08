/* global CKEDITOR */
/*
 * Sends Django's CSRF token with CKEditor 4 uploads (image dialog and
 * paste/drop), so the n1ed upload view keeps CSRF protection.
 */
;(function () {
  window.n1edCsrfToken = function (element) {
    var form = element && element.form
    var input = (form || document).querySelector("[name=csrfmiddlewaretoken]")
    if (input) return input.value
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)
    return match ? decodeURIComponent(match[1]) : ""
  }

  if (!window.CKEDITOR || CKEDITOR.n1edCsrf) return
  CKEDITOR.n1edCsrf = true

  CKEDITOR.on("instanceCreated", function (e) {
    var editor = e.editor
    editor.on("fileUploadRequest", function (evt) {
      var xhr = evt.data.fileLoader.xhr
      xhr.setRequestHeader("X-CSRFToken", window.n1edCsrfToken(editor.element.$))
      xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest")
    })
  })
})()
