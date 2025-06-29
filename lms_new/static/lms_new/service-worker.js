const CACHE_NAME = 'lms-cache-v1';
const urlsToCache = [
  '/',
  '/static/lms_new/theme.css',
  '/static/lms_new/manifest.json',
  '/static/lms_new/icons/icon-192.png',
  '/static/lms_new/icons/icon-512.png',
  // Add more static files as needed
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        return response || fetch(event.request);
      })
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.filter(function(cacheName) {
          return cacheName !== CACHE_NAME;
        }).map(function(cacheName) {
          return caches.delete(cacheName);
        })
      );
    })
  );
}); 