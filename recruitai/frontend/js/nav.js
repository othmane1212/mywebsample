/* RecruitAI — shared mobile navigation behavior
   Handles: topbar hamburger (public pages) + sidebar drawer (app pages) */
(function () {
  function initTopbarNav() {
    var toggle = document.getElementById("nav-toggle");
    var links = document.getElementById("nav-links");
    if (!toggle || !links) return;
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        links.classList.remove("open");
        toggle.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  function initSidebarDrawer() {
    var sidebar = document.querySelector(".sidebar");
    if (!sidebar) return;
    var toggle = document.getElementById("sidebar-toggle");
    var backdrop = document.getElementById("sidebar-backdrop");
    if (!toggle || !backdrop) return;
    function close() {
      sidebar.classList.remove("open");
      backdrop.classList.remove("open");
      toggle.classList.remove("is-hidden");
      toggle.setAttribute("aria-expanded", "false");
    }
    function open() {
      sidebar.classList.add("open");
      backdrop.classList.add("open");
      toggle.classList.add("is-hidden");
      toggle.setAttribute("aria-expanded", "true");
    }
    toggle.addEventListener("click", function () {
      if (sidebar.classList.contains("open")) close(); else open();
    });
    backdrop.addEventListener("click", close);
    var closeBtn = document.getElementById("sidebar-close");
    if (closeBtn) closeBtn.addEventListener("click", close);
    sidebar.querySelectorAll(".side-link").forEach(function (l) {
      l.addEventListener("click", close);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTopbarNav();
    initSidebarDrawer();
  });
})();
