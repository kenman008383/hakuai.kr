// 하쿠의 AI 첫걸음 — 화면 동작 (메뉴, 문장 복사, 연습 체크, 필터, 검색, 이어서 공부하기)
(function () {
  "use strict";
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("hakuai-" + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("hakuai-" + k, JSON.stringify(v)); } catch (e) {} }
  };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // 과정 메뉴 / 모바일 메뉴
  var mega = $("#mega"), ddBtn = $("#dd-btn"), sheet = $("#sheet"), menuBtn = $("#menu-btn");
  function closeMenus() {
    if (mega) { mega.hidden = true; ddBtn.setAttribute("aria-expanded", "false"); }
    if (sheet) { sheet.hidden = true; menuBtn.setAttribute("aria-expanded", "false"); }
  }
  if (ddBtn) ddBtn.addEventListener("click", function (e) {
    e.stopPropagation(); var open = mega.hidden; closeMenus(); mega.hidden = !open; ddBtn.setAttribute("aria-expanded", String(open));
  });
  if (menuBtn) menuBtn.addEventListener("click", function () {
    var open = sheet.hidden; sheet.hidden = !open; menuBtn.setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("click", function (e) { if (mega && !e.target.closest(".dd")) { mega.hidden = true; ddBtn.setAttribute("aria-expanded", "false"); } });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeMenus(); });

  // 문장 복사
  $$("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var el = document.getElementById(btn.getAttribute("data-copy"));
      var done = function () { btn.textContent = "복사했어요"; btn.classList.add("done"); setTimeout(function () { btn.textContent = "문장 복사"; btn.classList.remove("done"); }, 1800); };
      var fallback = function () { var r = document.createRange(); r.selectNodeContents(el); var s = getSelection(); s.removeAllRanges(); s.addRange(r); btn.textContent = "선택했어요 · 길게 눌러 복사"; };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(el.textContent).then(done, fallback); else fallback();
    });
  });

  // 강의 페이지: 연습 체크 저장, 최근 본 강의 기억, 모바일에서 목차 접기
  var lesson = $("[data-lesson]");
  if (lesson) {
    var slug = lesson.getAttribute("data-lesson");
    var checks = store.get("practice-" + slug, {});
    $$("[data-check]", lesson).forEach(function (box) {
      box.checked = !!checks[box.getAttribute("data-check")];
      box.addEventListener("change", function () { checks[box.getAttribute("data-check")] = box.checked; store.set("practice-" + slug, checks); });
    });
    var h1 = $("h1", lesson);
    store.set("recent", { url: location.pathname, title: h1 ? h1.textContent : "" });
    var toc = $("#toc");
    if (toc && window.matchMedia("(max-width: 760px)").matches) toc.open = false;
  }

  // 홈: 이어서 공부하기
  var start = $("#start-btn");
  if (start) {
    var recent = store.get("recent", null);
    if (recent && recent.url) { start.href = recent.url; start.textContent = "이어서 공부하기"; }
  }

  // 단계별 필터 (Q&A, 자료실)
  var filterBtns = $$("[data-filter]");
  if (filterBtns.length) {
    var items = $$("[data-level]");
    var empty = $("#qna-empty") || $("#res-empty");
    filterBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-filter"), shown = 0;
        filterBtns.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        items.forEach(function (it) { var on = f === "all" || it.getAttribute("data-level") === f; it.hidden = !on; if (on) shown++; });
        if (empty) empty.hidden = shown > 0;
      });
    });
  }

  // 검색 페이지
  var idxEl = $("#search-index");
  if (idxEl) {
    var index = JSON.parse(idxEl.textContent);
    var q = new URLSearchParams(location.search).get("q") || "";
    var input = $("#search-input"), out = $("#search-results"), status = $("#search-status");
    input.value = q;
    var esc = function (s) { return s.replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
    var run = function (term) {
      term = term.trim();
      if (!term) { status.textContent = "찾고 싶은 말을 입력해 주세요."; out.innerHTML = ""; return; }
      var words = term.split(/\s+/);
      var hits = index.filter(function (e) { return words.every(function (w) { return e.text.indexOf(w) >= 0; }); });
      status.textContent = hits.length ? "‘" + term + "’ 검색 결과 " + hits.length + "개" : "‘" + term + "’에 맞는 강의가 없어요. 다른 말로 찾아보세요.";
      out.innerHTML = hits.map(function (e) { return '<a href="' + e.url + '"><span class="meta"><span class="chip">' + esc(e.label) + '</span></span><b>' + esc(e.title) + "</b></a>"; }).join("");
    };
    run(q);
    input.addEventListener("input", function () { run(input.value); });
  }
})();
