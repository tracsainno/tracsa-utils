/* global CKEDITOR */
/*
 * CKEditor 4 throws "Cannot read properties of null (reading 'type')" in
 * range.createBookmark2() when a range offset points past the end of its
 * container. N1ED/ImgPen replaces nodes in the document and then fires
 * "saveSnapshot" with the stale selection, which breaks the undo snapshot and
 * the image update. Retry with offsets clamped to the container size.
 */
;(function () {
  if (!window.CKEDITOR || CKEDITOR.n1edBookmarkFix) return
  CKEDITOR.n1edBookmarkFix = true

  function maxOffset(node) {
    return node.type == CKEDITOR.NODE_ELEMENT ? node.getChildCount() : node.getLength()
  }

  var proto = CKEDITOR.dom.range.prototype
  var createBookmark2 = proto.createBookmark2

  proto.createBookmark2 = function () {
    try {
      return createBookmark2.apply(this, arguments)
    } catch (e) {
      var range = this.clone()
      range.setStart(range.startContainer, Math.min(range.startOffset, maxOffset(range.startContainer)))
      range.setEnd(range.endContainer, Math.min(range.endOffset, maxOffset(range.endContainer)))
      return createBookmark2.apply(range, arguments)
    }
  }

  // Empty <i>/<span> are icons (Font Awesome in N1ED blocks). CKEditor drops
  // them by default, which loses them whenever N1ED's cloud is unreachable.
  CKEDITOR.dtd.$removeEmpty.i = 0
  CKEDITOR.dtd.$removeEmpty.span = 0
})()
