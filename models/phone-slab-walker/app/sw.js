// 一度開けば、パソコンの線を抜いてもスマホだけで開けるようにする。
const CACHE = 'phone-slab-walker-1';
const FILES = ['./', './index.html', './brain.mjs', './transport.mjs', './manifest.webmanifest'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
    .then(() => self.clients.claim()));
});

// 繋がっていれば新しい版を取り、切れていれば手元の版を返す
self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request).then(response => {
    if (response.ok) {
      const copy = response.clone();
      caches.open(CACHE).then(cache => cache.put(event.request, copy));
    }
    return response;
  }).catch(() => caches.match(event.request)));
});
