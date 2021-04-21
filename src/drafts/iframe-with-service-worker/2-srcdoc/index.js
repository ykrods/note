const SUB_HTML = `<!doctype html>
<html>
  <head>
    <title>iframe with service worker</title>
    <meta charset="utf-8" />
    <script>
      console.log(location.toString()); // about:srcdoc
      console.log(location.origin);     // null

      // console.log(document.cookie)

      // const script = document.createElement("script");
      // script.innerHTML = "window.alert('jacked!')";
      // window.parent.document.body.append(script);

      // fetch("/index.html").then((response) => console.log(response));
    </script>
  </head>
  <body>
    srcdoc
  </body>
</html>`;


document.addEventListener("DOMContentLoaded", () => {
  const iframe = document.createElement('iframe');
  iframe.sandbox = "allow-scripts";
  // iframe.sandbox = "allow-same-origin";
  iframe.srcdoc = SUB_HTML;
  iframe.width= "100";
  iframe.height = "100";
  document.body.appendChild(iframe);
});
