// Basic Service Worker for PWA installation prompt
// This doesn't do any offline caching yet, but is needed for the install banner.

self.addEventListener('install', (event) => {
  console.log('Service Worker installing.');
  // Optionally, skip waiting to activate faster
  // self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating.');
});

self.addEventListener('fetch', (event) => {
  // Basic pass-through fetch handler.
  // For a real offline experience, you'd implement caching strategies here.
  event.respondWith(fetch(event.request));
});
