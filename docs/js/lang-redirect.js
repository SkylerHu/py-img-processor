document.addEventListener("DOMContentLoaded", function () {
  var STORAGE_KEY = "pyimgproc_lang_override";

  var switcher = document.querySelectorAll(".md-select__link[hreflang]");
  switcher.forEach(function (link) {
    link.addEventListener("click", function () {
      sessionStorage.setItem(STORAGE_KEY, link.getAttribute("hreflang"));
    });
  });

  var override = sessionStorage.getItem(STORAGE_KEY);
  if (override) return;

  var path = window.location.pathname;
  var isZh = /\/zh\//.test(path) || /\/zh$/.test(path);

  var ref = document.referrer;
  if (ref) {
    try {
      var refUrl = new URL(ref);
      if (refUrl.host === window.location.host) {
        var refIsZh = /\/zh\//.test(refUrl.pathname) || /\/zh$/.test(refUrl.pathname);
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
    var zhLink = document.querySelector('.md-select__link[hreflang="zh"]');
    if (zhLink && zhLink.href) {
      window.location.replace(zhLink.href);
    }
  }
});
