// App menu clicks: which app a visitor went to from here (no cookies, a per-session random id).
// Shared footer: the email link, and its labels in the page's language (also after a language toggle).
(function () {
  // footer labels (tools/app_menu.py)
  var SF = {"en":{support:"Support",privacy:"Privacy",terms:"Terms"},"ar":{support:"الدعم",privacy:"الخصوصية",terms:"الشروط"},"de":{support:"Support",privacy:"Datenschutz",terms:"Bedingungen"},"es":{support:"Soporte",privacy:"Privacidad",terms:"Términos"},"es-mx":{support:"Soporte",privacy:"Privacidad",terms:"Términos"},"fr":{support:"Assistance",privacy:"Confidentialité",terms:"Conditions"},"hi":{support:"सहायता",privacy:"गोपनीयता",terms:"शर्तें"},"id":{support:"Dukungan",privacy:"Privasi",terms:"Ketentuan"},"it":{support:"Supporto",privacy:"Privacy",terms:"Termini"},"ja":{support:"サポート",privacy:"プライバシー",terms:"利用規約"},"ko":{support:"지원",privacy:"개인정보",terms:"이용약관"},"nl":{support:"Support",privacy:"Privacy",terms:"Voorwaarden"},"pt-br":{support:"Suporte",privacy:"Privacidade",terms:"Termos"},"ru":{support:"Поддержка",privacy:"Конфиденциальность",terms:"Условия"},"sv":{support:"Support",privacy:"Integritet",terms:"Villkor"},"th":{support:"ฝ่ายสนับสนุน",privacy:"ความเป็นส่วนตัว",terms:"ข้อกำหนด"},"tr":{support:"Destek",privacy:"Gizlilik",terms:"Koşullar"},"vi":{support:"Hỗ trợ",privacy:"Quyền riêng tư",terms:"Điều khoản"},"zh-hans":{support:"支持",privacy:"隐私",terms:"条款"},"zh-hant":{support:"支援",privacy:"隱私權",terms:"條款"}};
  function lang() {
    var l = (document.documentElement.lang || "en").toLowerCase();
    if (SF[l]) return l;
    if (l.indexOf("pt") === 0) return "pt-br";
    if (l.indexOf("zh") === 0) return /hant|tw|hk|mo/.test(l) ? "zh-hant" : "zh-hans";
    l = l.split("-")[0];
    return SF[l] ? l : "en";
  }
  function footer() {
    var d = SF[lang()] || SF.en;
    if (!d) return;
    var els = document.querySelectorAll("footer.sf [data-sf]");
    for (var i = 0; i < els.length; i++) { var v = d[els[i].getAttribute("data-sf")]; if (v) els[i].textContent = v; }
  }
  var mails = document.querySelectorAll("footer.sf a.email[data-u]");
  for (var i = 0; i < mails.length; i++)
    mails[i].href = "mailto:" + mails[i].getAttribute("data-u") + String.fromCharCode(64) + mails[i].getAttribute("data-d");
  footer();
  try { new MutationObserver(footer).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] }); } catch (_) {}

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
