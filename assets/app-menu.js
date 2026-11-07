// App menu clicks: which app a visitor went to from here (no cookies, a per-session random id).
(function () {
  var SITE = location.hostname.replace(/^www\./, "") || "local";
  function sid() {
    try {
      var k = "sw_sid", v = sessionStorage.getItem(k);
      if (!v) { v = crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2); sessionStorage.setItem(k, v); }
      return v;
    } catch (_) { return "anon"; }
  }
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest && e.target.closest(".am a[data-app]");
    if (!a || a.hasAttribute("aria-current")) return;
    try {
      fetch("https://claude-proxy-web.ilbulyori.workers.dev/events", {
        method: "POST", keepalive: true,
        headers: { "content-type": "application/json", "x-device-id": sid() },
        body: JSON.stringify({
          meta: { app: SITE, build: "web", os: "web", locale: (navigator.language || "").slice(0, 8) },
          events: [{ name: "menu_click", ts: Date.now() / 1000,
            props: { site: SITE, to: a.dataset.app, path: location.pathname.slice(0, 64) } }]
        })
      }).catch(function () {});
    } catch (_) {}
  }, true);
})();
