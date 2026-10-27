/* Contents-rail scrollspy.
 *
 * The rail highlights the section the reader is in. Sections are tracked by
 * intersection rather than by scroll offset so nothing runs on the scroll
 * event; when several are on screen at once the earliest in document order
 * wins, which is what the rail reads like when you scroll slowly through a
 * boundary.
 */
(function () {
  "use strict";

  var links = Array.prototype.slice.call(document.querySelectorAll("[data-navlink]"));
  var sections = Array.prototype.slice.call(document.querySelectorAll("[data-spy]"));
  if (!links.length || !sections.length || !("IntersectionObserver" in window)) return;

  var order = sections.map(function (s) { return s.getAttribute("data-spy"); });
  var visible = {};

  function paint(id) {
    links.forEach(function (a) {
      var on = a.getAttribute("data-navlink") === id;
      a.classList.toggle("is-active", on);
      if (on) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      visible[e.target.getAttribute("data-spy")] = e.isIntersecting;
    });

    for (var i = 0; i < order.length; i++) {
      if (visible[order[i]]) { paint(order[i]); return; }
    }
  }, {
    // Top inset clears the fixed bar; the bottom inset keeps a section from
    // claiming the rail while it is still only peeking in from below.
    rootMargin: "-84px 0px -55% 0px",
    threshold: 0
  });

  sections.forEach(function (s) { io.observe(s); });
})();
