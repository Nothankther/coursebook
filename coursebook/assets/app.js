/* coursebook 前端：目录、搜索、进度、打印。无依赖。 */
(function () {
  'use strict';

  var chapters = [].slice.call(document.querySelectorAll('section.chapter'));
  var toc = document.getElementById('toc');
  var KEY = 'coursebook:done:' + location.pathname;

  /* ---------- 目录 ---------- */
  var links = [];
  chapters.forEach(function (ch) {
    var num = ch.getAttribute('data-num') || '';
    var title = ch.getAttribute('data-title') || '';
    var short = ch.getAttribute('data-short') || title;
    var a = document.createElement('a');
    a.href = '#' + ch.id;
    a.setAttribute('data-target', ch.id);
    a.innerHTML = '<span class="num">' + (num.length < 2 ? '0' + num : num) + '</span>' +
      '<span class="lbl">' + short + '</span>' +
      '<span class="tick" data-ch="' + ch.id + '" title="标记已复习"></span>';
    toc.appendChild(a);
    links.push(a);
  });

  /* ---------- 进度条与高亮 ---------- */
  var bar = document.getElementById('progress');
  var ticking = false;

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      if (bar) bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';

      var y = h.scrollTop + 120;
      for (var i = links.length - 1; i >= 0; i--) {
        var el = document.getElementById(links[i].getAttribute('data-target'));
        if (el && el.offsetTop <= y) {
          links.forEach(function (l) { l.classList.remove('on'); });
          links[i].classList.add('on');
          break;
        }
      }
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- 已复习勾选 ---------- */
  var done = {};
  try { done = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { done = {}; }

  function refreshDone() {
    var total = chapters.length;
    var n = 0;
    chapters.forEach(function (ch) {
      var tick = toc.querySelector('.tick[data-ch="' + ch.id + '"]');
      if (done[ch.id]) { n++; if (tick) tick.classList.add('on'); }
      else if (tick) tick.classList.remove('on');
    });
    var c = document.getElementById('doneCount');
    if (c) c.textContent = n + '/' + total;
    var ring = document.getElementById('doneRing');
    if (ring) ring.style.background = 'conic-gradient(#0f766e ' + (total ? n / total * 100 : 0) + '%,#e2e8f0 0)';
  }
  toc.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('.tick') : null;
    if (!t) return;
    e.preventDefault();
    e.stopPropagation();
    var id = t.getAttribute('data-ch');
    done[id] = !done[id];
    try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (err) {}
    refreshDone();
  });
  refreshDone();

  /* ---------- 移动端菜单 ---------- */
  var btn = document.getElementById('menuBtn');
  if (btn) btn.addEventListener('click', function () {
    document.body.classList.toggle('menu-open');
  });
  toc.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('a')) document.body.classList.remove('menu-open');
  });

  /* ---------- 搜索：首次输入时建索引，避免在 MathJax 排版前抓取 ---------- */
  var input = document.getElementById('q');
  var panel = null;
  var index = null;

  function buildIndex() {
    if (index) return index;
    index = [];
    chapters.forEach(function (ch) {
      var walker = document.createTreeWalker(ch, NodeFilter.SHOW_TEXT, null);
      var buf = [];
      var node;
      while ((node = walker.nextNode())) {
        var p = node.parentNode;
        if (!p || p.closest('script,style,.tick,.toc')) continue;
        var txt = (node.nodeValue || '').trim();
        if (txt) buf.push(txt);
      }
      var text = buf.join(' ');
      index.push({ id: ch.id, title: ch.getAttribute('data-title') || '', text: text });
    });
    return index;
  }

  function showResults(kw) {
    if (!panel) {
      panel = document.createElement('div');
      panel.className = 'search-panel';
      document.querySelector('.searchbox').appendChild(panel);
    }
    kw = kw.trim().toLowerCase();
    if (!kw) { panel.classList.remove('on'); panel.innerHTML = ''; return; }
    var idx = buildIndex();
    var hits = [];
    idx.forEach(function (c) {
      var pos = c.text.toLowerCase().indexOf(kw);
      if (c.title.toLowerCase().indexOf(kw) >= 0 || pos >= 0) {
        var snip = pos >= 0 ? c.text.slice(Math.max(0, pos - 24), pos + 60) : c.text.slice(0, 80);
        hits.push({ id: c.id, title: c.title, snip: snip });
      }
    });
    panel.innerHTML = hits.length
      ? hits.slice(0, 8).map(function (h) {
          return '<a href="#' + h.id + '"><b>' + h.title + '</b><span>' + h.snip + '…</span></a>';
        }).join('')
      : '<div class="empty">没有匹配的章节</div>';
    panel.classList.add('on');
  }

  if (input) {
    input.addEventListener('input', function () { showResults(this.value); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { this.value = ''; showResults(''); this.blur(); }
      if (e.key === 'Enter' && panel) {
        var first = panel.querySelector('a');
        if (first) location.hash = first.getAttribute('href');
      }
    });
    document.addEventListener('click', function (e) {
      if (panel && !e.target.closest('.searchbox')) panel.classList.remove('on');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== input) { e.preventDefault(); input.focus(); }
    });
  }

  /* ---------- 工具按钮 ---------- */
  var btnAll = document.getElementById('btnAll');
  if (btnAll) btnAll.addEventListener('click', function () {
    var all = [].slice.call(document.querySelectorAll('.example details'));
    var closed = all.some(function (d) { return !d.open; });
    all.forEach(function (d) { d.open = closed; });
    this.classList.toggle('on', closed);
  });

  var btnPrint = document.getElementById('btnPrint');
  if (btnPrint) btnPrint.addEventListener('click', function () {
    [].slice.call(document.querySelectorAll('.example details')).forEach(function (d) { d.open = true; });
    window.print();
  });

  var reopened = [];
  window.addEventListener('beforeprint', function () {
    reopened = [];
    [].slice.call(document.querySelectorAll('.example details')).forEach(function (d) {
      if (!d.open) { d.open = true; reopened.push(d); }
    });
  });
  window.addEventListener('afterprint', function () {
    reopened.forEach(function (d) { d.open = false; });
  });

  var top = document.getElementById('btnTop');
  if (top) top.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();
