"""آیکن و تنظیمات نصب روی گوشی (PWA).

- آیکن تب/میان‌بر از static/icon-512.png گرفته می‌شود (در app.py).
- این ماژول تلاش می‌کند manifest و رنگ نوار بالا را به صفحهٔ میزبان اضافه کند.
  اگر مرورگر یا Streamlit Cloud اجازه ندهد، بی‌صدا رد می‌شود و برنامه عادی کار می‌کند.
"""
import streamlit.components.v1 as components

_JS = """
<script>
(function () {
  var base = '/app/static/';
  var targets = [];
  try { targets.push(window.parent.document); } catch (e) {}
  try { targets.push(window.top.document); } catch (e) {}
  targets.forEach(function (doc) {
    try {
      var head = doc.head;
      if (!head || head.querySelector('link[data-sade]')) return;
      head.querySelectorAll('link[rel="manifest"]').forEach(function (l) { l.remove(); });
      function add(tag, attrs) {
        var el = doc.createElement(tag);
        for (var k in attrs) el.setAttribute(k, attrs[k]);
        el.setAttribute('data-sade', '1');
        head.appendChild(el);
      }
      add('link', {rel: 'manifest', href: base + 'manifest.json'});
      add('link', {rel: 'apple-touch-icon', href: base + 'apple-touch-icon.png'});
      add('link', {rel: 'icon', type: 'image/png', sizes: '512x512', href: base + 'icon-512.png'});
      var m = head.querySelector('meta[name="theme-color"]');
      if (m) m.setAttribute('content', '#060a14'); else add('meta', {name: 'theme-color', content: '#060a14'});
    } catch (e) {}
  });
})();
</script>
"""


def inject_pwa():
    components.html(_JS, height=0)
