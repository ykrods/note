self.addEventListener('install', (event) => {
  console.log("install");
});

self.addEventListener('activate', (event) => {
  console.log("activate");
});

self.addEventListener('fetch', (event) => {
  console.log(event.request.url);
  const url = new URL(event.request.url);

  if (url.origin === location.origin && url.pathname === "/circle.svg") {
    event.respondWith(fetch("/circle-red.svg"));
  }
});
