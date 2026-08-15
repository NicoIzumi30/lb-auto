const CACHE = "lb-auto-shell-v24";
const ASSETS = ["./", "./index.html", "./styles.css?v=24", "./app.js?v=24", "./manifest.webmanifest?v=24", "./assets/logo.png", "./assets/cars/fortuner.webp", "./assets/cars/c200.webp", "./assets/cars/bmw-x3.webp", "./assets/cars/crv.webp", "./assets/cars/lexus-rx.webp", "./assets/cars/alphard.webp"];

self.addEventListener("install", (event) => event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting())));
self.addEventListener("activate", (event) => event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener("message", (event) => { if (event.data?.type === "SKIP_WAITING") self.skipWaiting(); });
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.pathname.startsWith("/api/")) return;
  event.respondWith(fetch(event.request).then((response) => {
    const copy = response.clone();
    caches.open(CACHE).then((cache) => cache.put(event.request, copy));
    return response;
  }).catch(() => caches.match(event.request).then((cached) => cached || caches.match("./index.html"))));
});
