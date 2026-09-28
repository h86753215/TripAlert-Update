(function () {
  if (window.__htaAnalyticsLoaded) return;
  window.__htaAnalyticsLoaded = true;

  window.va = window.va || function () {
    (window.vaq = window.vaq || []).push(arguments);
  };

  var script = document.createElement("script");
  script.defer = true;
  script.src = "/_vercel/insights/script.js";
  document.head.appendChild(script);

  function cleanLabel(node) {
    return String((node && node.textContent) || "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 72);
  }

  function track(name, data) {
    try {
      window.va("event", { name: name, data: data || {} });
    } catch (_) {}
  }

  document.addEventListener("click", function (event) {
    var target = event.target && event.target.closest
      ? event.target.closest("a,button")
      : null;
    if (!target) return;

    var href = target.getAttribute("href") || "";
    var label = cleanLabel(target);
    var page = location.pathname || "/";

    if (target.id === "apkDownload" || /\.apk(?:$|[?#])/i.test(href)) {
      track("APK Download", { page: page, item: "Android APK" });
    }

    if (/https?:\/\/lin\.ee\//i.test(href)) {
      track("LINE Click", { page: page, label: label || "LINE" });
    }

    if (
      /#trial-start\b/i.test(href) ||
      /48\s*小時.*試用|免費試用|申請試用|試用流程/.test(label)
    ) {
      track("Trial CTA", { page: page, label: label || "Trial" });
    }
  }, true);
})();
