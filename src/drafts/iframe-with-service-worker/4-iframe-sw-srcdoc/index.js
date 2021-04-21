const SUB_HTML = `<!doctype html>
<html>
  <head>
    <title>iframe with service worker</title>
    <meta charset="utf-8" />
    <script>
      console.log(location.origin);
      console.log(navigator.serviceWorker.controller);
      // window.parent.document.body.append("child injection");
    </script>
  </head>
  <body>
    <img src="/circle.svg"/>
  </body>
</html>`;

navigator.serviceWorker.register('/sw.js');

document.addEventListener("DOMContentLoaded", () => {
  const iframe = document.createElement('iframe');
  // iframe.sandbox = "allow-scripts";
  // iframe.sandbox = "allow-same-origin";
  iframe.srcdoc = SUB_HTML;
  iframe.width= "100";
  iframe.height = "100";
  document.body.appendChild(iframe);
});
