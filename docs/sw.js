// service worker حداقلی: فقط برای شرط نصب؛ همه‌چیز از شبکه گرفته می‌شود (بدون کش، تا داده‌ها قدیمی نشوند)
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', function (e) { e.respondWith(fetch(e.request)); });
