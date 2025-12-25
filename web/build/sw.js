if (!self.define) {
  let e,
    s = {};
  const i = (i, n) => (
    (i = new URL(i + ".js", n).href),
    s[i] ||
      new Promise((s) => {
        if ("document" in self) {
          const e = document.createElement("script");
          ((e.src = i), (e.onload = s), document.head.appendChild(e));
        } else ((e = i), importScripts(i), s());
      }).then(() => {
        let e = s[i];
        if (!e) throw new Error(`Module ${i} didn’t register its module`);
        return e;
      })
  );
  self.define = (n, r) => {
    const o =
      e ||
      ("document" in self ? document.currentScript.src : "") ||
      location.href;
    if (s[o]) return;
    let c = {};
    const d = (e) => i(e, o),
      t = { module: { uri: o }, exports: c, require: d };
    s[o] = Promise.all(n.map((e) => t[e] || d(e))).then((e) => (r(...e), c));
  };
}
define(["./workbox-8c29f6e4"], function (e) {
  "use strict";
  (self.skipWaiting(),
    e.clientsClaim(),
    e.precacheAndRoute(
      [
        { url: "registerSW.js", revision: "1872c500de691dce40960bb85481de07" },
        {
          url: "manifest.webmanifest",
          revision: "bd3f5fd8783bb6eca096cd786dadcb45",
        },
        { url: "index.js", revision: "f53c43c18fca26b503acbe3161331409" },
        { url: "index.html", revision: "ebd17c39b74b2d41ddcea13d29c1d4a9" },
        { url: "index.css", revision: "03062e5a8ac441fd05a23639121cc0b1" },
        { url: "assets/icon.svg", revision: null },
        { url: "assets/icon-512x512.png", revision: null },
        { url: "assets/icon-192x192.png", revision: null },
        { url: "assets/favicon.ico", revision: null },
        { url: "assets/apple-touch-icon.png", revision: null },
        {
          url: "assets/icon-192x192.png",
          revision: "d6d66f41ae2e454bd445b5b47098551d",
        },
        {
          url: "assets/icon-512x512.png",
          revision: "2b988f80dd851154a01df4a7f026ed9a",
        },
        {
          url: "manifest.webmanifest",
          revision: "bd3f5fd8783bb6eca096cd786dadcb45",
        },
      ],
      {},
    ),
    e.cleanupOutdatedCaches(),
    e.registerRoute(
      new e.NavigationRoute(e.createHandlerBoundToURL("index.html")),
    ));
});
