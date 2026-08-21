(function () {
  var STORAGE_KEY = "pyimgproc_lang_override";
  var override = localStorage.getItem(STORAGE_KEY);
  if (override) return;

  var path = window.location.pathname;
  var isZh = path.indexOf("/zh/") === 0 || path === "/zh";
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
      localStorage.setItem(STORAGE_KEY, link.getAttribute("hreflang"));
    });
  });
});
