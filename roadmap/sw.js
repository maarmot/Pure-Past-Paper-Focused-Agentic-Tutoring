// Bump this identifier when changing an application file. Cache only the public shell.
const cachePrefix = "ppp-fieldnotes-shell-" + self.registration.scope + "|";
const version = cachePrefix + "v1.0";
const files = [
  "index.html",
  "style.css",
  "mark.svg",
  "boot.mjs",
  "app.mjs",
  "map.mjs",
  "model.mjs",
  "curriculum.mjs",
];
const urls = files.map((name) => new URL(name, self.registration.scope).href);
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(version).then(async (cache) => {
      await cache.addAll(
        urls.map((url) => new Request(url, { cache: "reload" })),
      );
      await self.skipWaiting();
    }),
  );
});
self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      for (const name of await caches.keys())
        if (name.startsWith(cachePrefix) && name !== version)
          await caches.delete(name);
      await self.clients.claim();
    })(),
  );
});
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = event.request.url;
  const canonical = url === self.registration.scope ? urls[0] : url;
  if (!urls.includes(canonical)) return;
  event.respondWith(
    caches
      .open(version)
      .then(
        async (cache) => (await cache.match(canonical)) || fetch(event.request),
      ),
  );
});
