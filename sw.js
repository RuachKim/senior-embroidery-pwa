const CACHE_NAME = 'embroidery-pwa-cache-v1';
const urlsToCache = [
  './',
  './index.html',
  './icon.svg',
  './app.py',
  './digitizer.py',
  './manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response; // Cache hit
        }
        return fetch(event.request);
      })
  );
});