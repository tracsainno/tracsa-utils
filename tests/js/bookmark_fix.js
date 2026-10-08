// Usage: node bookmark_fix.js <ckeditor.js> <fixups.js>
// Prints the createBookmark2() result for a range whose offset is past the
// end of its container, before and after loading fixups.js.
const fs = require('fs')
const { JSDOM } = require('jsdom')

const [ckeditorPath, fixupsPath] = process.argv.slice(2)
const { window } = new JSDOM('<div id="root"><p>a</p></div>', {
  runScripts: 'outside-only',
  url: 'http://localhost/',
})
window.CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
window.eval(fs.readFileSync(ckeditorPath, 'utf8'))

function bookmark() {
  const root = new window.CKEDITOR.dom.element(window.document.getElementById('root'))
  const range = new window.CKEDITOR.dom.range(root)
  range.setStart(root, 3)
  range.setEnd(root, 3)
  try {
    return { bookmark: range.createBookmark2(true) }
  } catch (e) {
    return { error: e.message }
  }
}

const before = bookmark()
window.eval(fs.readFileSync(fixupsPath, 'utf8'))
console.log(JSON.stringify({ before, after: bookmark() }))
