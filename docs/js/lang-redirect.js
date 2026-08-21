(function () {
  var STORAGE_KEY = "pyimgproc_lang_override";
  var override = sessionStorage.getItem(STORAGE_KEY);
  if (override) return;

  var path = window.location.pathname;
  var isZh = path.indexOf("/zh/") === 0 || path === "/zh";

  var ref = document.referrer;
  if (ref) {
    try {
      var refUrl = new URL(ref);
      if (refUrl.host === window.location.host) {
        var refIsZh = refUrl.pathname.indexOf("/zh/") === 0 || refUrl.pathname === "/zh";
        if (refIsZh !== isZh) {
          sessionStorage.setItem(STORAGE_KEY, isZh ? "zh" : "en");
          return;
        }
      }
    } catch (e) {}
  }

  var browserLang = (navigator.language || navigator.userLanguage || "").toLowerCase();
  var wantZh = browserLang.indexOf("zh") === 0;

  if (wantZh && !isZh) {
    window.location.replace("/zh" + path);
  }
})();

document.addEventListener("DOMContentLoaded", function () {
  var STORAGE_KEY = "pyimgproc_lang_override";
  var switcher = document.querySelectorAll(".md-select__link[hreflang]");
  switcher.forEach(function (link) {
    link.addEventListener("click", function () {
      sessionStorage.setItem(STORAGE_KEY, link.getAttribute("hreflang"));
    });
  });
});
