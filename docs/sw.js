// service worker: پوستهٔ برنامه (همین صفحه و آیکن‌ها) برای حالت آفلاین کش می‌شود.
// درخواست‌های برنامهٔ Streamlit (دامنهٔ دیگر) دست‌کاری نمی‌شوند؛ پس داده‌های زندهٔ برنامه هرگز از کش نمی‌آیند.
var CACHE = 'sade-shell-v2';
var SHELL = ['./', 'index.html', 'manifest.json', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(SHELL); }).catch(function () {}));
  self.skipWaiting();
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  e.respondWith(
    fetch(req).then(function (res) {
      if (res && res.ok) { var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(req, copy); }); }
      return res;
    }).catch(function () {
      return caches.match(req).then(function (r) { return r || caches.match('index.html') || caches.match('./'); });
    })
  );
});
