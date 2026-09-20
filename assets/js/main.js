/* ============================================================================
 * Скрипт сайта: переключатель темы + мобильное меню.
 *
 * Заменяет assets/js/main.js темы nomad-tech (particles, свайп-навигация по
 * «секциям» и SPA-логика к этой верстке не относятся и только шумели бы).
 *
 * Тема хранится в localStorage ('prefer-theme'), класс .theme--dark вешается
 * на <body> — от него зависят токены в assets/scss/main.scss.
 * ========================================================================== */
(function () {
  'use strict';

  var DARK = 'theme--dark';
  var LIGHT = 'theme--light';
  var KEY = 'prefer-theme';
  var body = document.body;

  /* --- 1. Тема ---------------------------------------------------------- */
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}

  if (saved === DARK) {
    body.classList.add(DARK);
  } else if (saved !== LIGHT && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    body.classList.add(DARK);
  }

  var toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var dark = body.classList.toggle(DARK);
      try { localStorage.setItem(KEY, dark ? DARK : LIGHT); } catch (e) {}
    });
  }

  /* --- 2. Мобильное меню ------------------------------------------------ */
  var nav = document.getElementById('site-nav');
  var navToggle = document.querySelector('[data-nav-toggle]');

  function closeNav() {
    if (!nav) return;
    nav.setAttribute('data-open', 'false');
    if (navToggle) navToggle.setAttribute('aria-expanded', 'false');
  }

  if (nav && navToggle) {
    navToggle.addEventListener('click', function () {
      var open = nav.getAttribute('data-open') !== 'true';
      nav.setAttribute('data-open', open ? 'true' : 'false');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeNav();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeNav();
    });
  }

  /* --- 3. Якорные ссылки: отступ под «липкую» шапку --------------------- */
  document.querySelectorAll('a[href^="/#"], a[href^="#"], a[href^="/en/#"]').forEach(function (link) {
    link.addEventListener('click', function () {
      var id = link.getAttribute('href').split('#')[1];
      var target = id ? document.getElementById(id) : null;
      if (target) {
        target.style.scrollMarginTop = '80px';
      }
    });
  });
})();
