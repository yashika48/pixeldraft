/* preview.js — render generated React in a sandboxed iframe.
   Passes code via a JSON script block (no escaping issues), compiles with Babel,
   and shows any error inside the box. */

export function buildPreviewHtml(componentCode) {
  let body = (componentCode || "")
    .replace(/^\s*import\s.*$/gm, "")
    .replace(/export\s+default\s+function/g, "function")
    .replace(/export\s+default\s+/g, "")
    .replace(/\bexport\s+/g, "");

  // JSON.stringify safely encodes the code; we read it back inside the iframe.
  const payload = JSON.stringify(body);

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body{margin:0;padding:16px;background:#fff;font-family:Inter,system-ui,sans-serif}
  .pd-err{color:#b91c1c;font-family:monospace;font-size:12px;white-space:pre-wrap}</style>
</head>
<body>
  <div id="root"></div>
  <script id="pd-code" type="application/json">${payload}</script>
  <script>
    (function () {
      function show(msg){ document.getElementById('root').innerHTML =
        '<div class="pd-err">Preview error:\\n' + msg + '</div>'; }
      try {
        var src = JSON.parse(document.getElementById('pd-code').textContent);
        var out = Babel.transform(src, { presets: ['react'] }).code;
        var fn = new Function('React', 'ReactDOM', out + '\\nreturn GeneratedUI;');
        var Comp = fn(React, ReactDOM);
        ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(Comp));
      } catch (e) { show(e && e.message ? e.message : String(e)); }
    })();
  </script>
</body>
</html>`;
}