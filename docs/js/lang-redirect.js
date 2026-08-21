/**
 * 浏览器语言自动跳转脚本。
 *
 * 首次访问时，根据浏览器语言设置自动跳转到对应的语言版本。
 * 跳转 URL 从 Material 主题的语言切换器获取（使用相对路径，兼容 Read the Docs 多版本）。
 *
 * 使用 sessionStorage 记录用户主动切换语言的行为，防止自动跳转覆盖用户选择。
 * 标签页关闭后记录清除，下次访问重新按浏览器语言跳转。
 */
document.addEventListener("DOMContentLoaded", function () {
  var STORAGE_KEY = "pyimgproc_lang_override";

  // 监听 Material 主题语言切换器的点击，记录用户主动选择
  var switcher = document.querySelectorAll(".md-select__link[hreflang]");
  switcher.forEach(function (link) {
    link.addEventListener("click", function () {
      sessionStorage.setItem(STORAGE_KEY, link.getAttribute("hreflang"));
    });
  });

  // 已有用户主动选择的记录，跳过自动跳转
  var override = sessionStorage.getItem(STORAGE_KEY);
  if (override) return;

  // 检测当前页面是否在中文版本路径下（匹配任意位置的 /zh/，兼容多版本 URL）
  var path = window.location.pathname;
  var isZh = /\/zh\//.test(path) || /\/zh$/.test(path);

  // 通过 referrer 检测用户从站内跨语言导航（如从 /zh/ 点击到 /en/），
  // 视为主动切换，设置覆盖标记并跳过自动跳转
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

  // 浏览器语言为中文但当前不在中文版本，自动跳转到中文
  var browserLang = (navigator.language || navigator.userLanguage || "").toLowerCase();
  var wantZh = browserLang.indexOf("zh") === 0;

  if (wantZh && !isZh) {
    var zhLink = document.querySelector('.md-select__link[hreflang="zh"]');
    if (zhLink && zhLink.href) {
      window.location.replace(zhLink.href);
    }
  }
});
