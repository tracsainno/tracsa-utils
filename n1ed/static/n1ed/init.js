/* global CKEDITOR, tinymce */
/*
 * Starts the editors rendered by n1ed.widgets.N1EDEditorWidget subclasses. Each textarea carries:
 *   data-n1ed-editor   "ckeditor4" or "tinymce"
 *   data-n1ed-scripts  JSON list of scripts to load first (in order)
 *   data-n1ed-config   JSON editor config
 *   data-n1ed-upload   upload URL (optional)
 */
;(function () {
  var loading = {}

  function loadScript(src) {
    if (!loading[src]) {
      loading[src] = new Promise(function (resolve, reject) {
        var script = document.createElement("script")
        script.src = src
        script.onload = resolve
        script.onerror = function () { reject(new Error("Cannot load " + src)) }
        document.head.appendChild(script)
      })
    }
    return loading[src]
  }

  function loadScripts(srcs) {
    return srcs.reduce(function (chain, src) {
      return chain.then(function () { return loadScript(src) })
    }, Promise.resolve())
  }

  function uploadHandler(textarea, url) {
    // TinyMCE: same request as its default handler, plus the CSRF token.
    return function (blobInfo, progress) {
      return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest()
        xhr.open("POST", url)
        xhr.setRequestHeader("X-CSRFToken", window.n1edCsrfToken(textarea))
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest")
        xhr.upload.onprogress = function (e) { progress(e.loaded / e.total * 100) }
        xhr.onload = function () {
          var json = null
          try { json = JSON.parse(xhr.responseText) } catch (e) {}
          if (xhr.status >= 200 && xhr.status < 300 && json && json.location) {
            resolve(json.location)
          } else {
            var message = json && json.error ? json.error.message : "HTTP error " + xhr.status
            reject({ message: message, remove: true })
          }
        }
        xhr.onerror = function () { reject({ message: "Upload failed", remove: true }) }
        var data = new FormData()
        data.append("file", blobInfo.blob(), blobInfo.filename())
        xhr.send(data)
      })
    }
  }

  var starters = {
    ckeditor4: function (textarea, config) {
      CKEDITOR.replace(textarea, config)
    },
    tinymce: function (textarea, config, upload) {
      config.target = textarea
      if (upload) config.images_upload_handler = uploadHandler(textarea, upload)
      tinymce.init(config)
    },
  }

  function start(textarea) {
    if (textarea.getAttribute("data-n1ed-processed") || textarea.id.indexOf("__prefix__") !== -1) return
    textarea.setAttribute("data-n1ed-processed", "1")
    var editor = textarea.getAttribute("data-n1ed-editor")
    var config = JSON.parse(textarea.getAttribute("data-n1ed-config"))
    var upload = textarea.getAttribute("data-n1ed-upload")
    var scripts = JSON.parse(textarea.getAttribute("data-n1ed-scripts"))
    if (editor === "ckeditor4" && !window.CKEDITOR_BASEPATH) {
      window.CKEDITOR_BASEPATH = textarea.getAttribute("data-n1ed-basepath")
    }
    loadScripts(scripts)
      .then(function () { starters[editor](textarea, config, upload) })
      .catch(function (e) { console.error("[n1ed]", e) })
  }

  function startAll() {
    var textareas = document.querySelectorAll("textarea[data-n1ed-editor]")
    for (var i = 0; i < textareas.length; i++) start(textareas[i])
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startAll)
  } else {
    startAll()
  }
  // Admin inlines added with "Add another".
  document.addEventListener("formset:added", startAll)
  if (window.django && django.jQuery) django.jQuery(document).on("formset:added", startAll)
})()
