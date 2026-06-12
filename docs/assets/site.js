// AVIATOR — minimal site interactions (no dependencies)
(function () {
  var noMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // mobile nav
  var burger = document.querySelector('.nav-burger');
  var nav = document.querySelector('.nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', nav.classList.contains('open'));
    });
  }

  // generic crossfade carousel: dots + arrows + swipe + autoplay
  function carousel(root, slideSel, dotSel, interval, onShow) {
    if (!root) return;
    var slides = root.querySelectorAll(slideSel);
    var dots = root.querySelectorAll(dotSel + ' button');
    if (slides.length < 2) return;
    var i = 0, timer;
    function show(n) {
      slides[i].classList.remove('on');
      if (dots[i]) dots[i].classList.remove('on');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('on');
      if (dots[i]) dots[i].classList.add('on');
      if (onShow) onShow(slides[i]);
    }
    function start() {
      if (!noMotion) timer = setInterval(function () { show(i + 1); }, interval);
    }
    function bump(n) { clearInterval(timer); show(n); start(); }
    dots.forEach(function (d, n) {
      d.addEventListener('click', function () { bump(n); });
    });
    var nx = root.querySelector('.car-next'), pv = root.querySelector('.car-prev');
    if (nx) nx.addEventListener('click', function () { bump(i + 1); });
    if (pv) pv.addEventListener('click', function () { bump(i - 1); });
    var x0 = null;
    root.addEventListener('pointerdown', function (e) { x0 = e.clientX; });
    root.addEventListener('pointerup', function (e) {
      if (x0 === null) return;
      var dx = e.clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 40) bump(i + (dx < 0 ? 1 : -1));
    });
    root.addEventListener('mouseenter', function () { clearInterval(timer); });
    root.addEventListener('mouseleave', function () { clearInterval(timer); start(); });
    start();
  }

  // hero: caption follows the slide
  var heroCap = document.querySelector('.hero-cap');
  carousel(document.querySelector('.hero-car'), '.hs', '.hero-dots', 5200, function (slide) {
    if (!heroCap) return;
    heroCap.classList.add('fade');
    setTimeout(function () {
      heroCap.textContent = slide.dataset.cap || '';
      heroCap.classList.remove('fade');
    }, 300);
  });

  // spotlight: whole text block follows the slide
  var spotBody = document.querySelector('.spot-body');
  carousel(document.querySelector('.spot-car'), '.ss', '.spot-dots', 6500, function (slide) {
    if (!spotBody) return;
    var d = slide.dataset;
    spotBody.classList.add('swap');
    setTimeout(function () {
      spotBody.querySelector('.kicker').textContent = d.kick;
      spotBody.querySelector('h2').textContent = d.title;
      spotBody.querySelector('p').textContent = d.text;
      var b = spotBody.querySelector('.btn');
      b.textContent = d.btn;
      b.setAttribute('href', d.href);
      spotBody.classList.remove('swap');
    }, 320);
  });

  // flight path: plane rides the curve as you scroll, drawing a contrail
  var fp = document.querySelector('.flightpath');
  if (fp && !noMotion) {
    var track = fp.querySelector('.fp-track');
    var trail = fp.querySelector('.fp-trail');
    var fpg = fp.querySelector('.fpg');
    var L = track.getTotalLength();
    trail.style.strokeDasharray = L;
    trail.style.strokeDashoffset = L;
    var ticking = false;
    var fpUpdate = function () {
      ticking = false;
      var r = fp.getBoundingClientRect();
      var vh = window.innerHeight || 1;
      var p = (vh - r.top) / (vh + r.height);
      p = Math.max(0, Math.min(1, p * 1.5 - 0.25));
      var len = p * L;
      var pt = track.getPointAtLength(len);
      var ahead = track.getPointAtLength(Math.min(L, len + 2));
      var a = Math.atan2(ahead.y - pt.y, ahead.x - pt.x) * 180 / Math.PI;
      fpg.setAttribute('transform',
        'translate(' + pt.x.toFixed(1) + ' ' + pt.y.toFixed(1) + ') rotate(' + (a + 90).toFixed(1) + ')');
      trail.style.strokeDashoffset = L - len;
    };
    var fpScroll = function () {
      if (!ticking) { ticking = true; requestAnimationFrame(fpUpdate); }
    };
    addEventListener('scroll', fpScroll, { passive: true });
    addEventListener('resize', fpScroll, { passive: true });
    fpUpdate();
  }

  // page-long sky path: built in pixel coords, drawn by scroll
  var sky = document.querySelector('.skypath');
  if (sky && !noMotion) {
    var sSvg = sky.querySelector('svg');
    var sTrack = sky.querySelector('.sp-track');
    var sTrail = sky.querySelector('.sp-trail');
    var sPlane = document.querySelector('.skyplane');
    var sL = 0, sTop = 0;
    var skyUpdate = function () {
      if (!sL) return;
      var r = sky.getBoundingClientRect();
      var p = ((window.innerHeight || 1) * 0.65 - r.top) / r.height;
      p = Math.max(0, Math.min(1, p));
      var len = p * sL;
      var pt = sTrack.getPointAtLength(len);
      var ahead = sTrack.getPointAtLength(Math.min(sL, len + 2));
      var a = Math.atan2(ahead.y - pt.y, ahead.x - pt.x) * 180 / Math.PI;
      if (sPlane) {
        sPlane.style.transform = 'translate(' + (pt.x - 22).toFixed(1) + 'px,'
          + (sTop + pt.y - 22).toFixed(1) + 'px) rotate(' + (a + 90).toFixed(1) + 'deg)';
      }
      sTrail.style.strokeDashoffset = sL - len;
    };
    var skyBuild = function () {
      var sv = document.getElementById('services');
      var cta = document.querySelector('.cta-band');
      if (!sv || !cta) return;
      var top = sv.getBoundingClientRect().top + window.scrollY - 30;
      var end = cta.getBoundingClientRect().top + window.scrollY - 24;
      var Hh = end - top;
      if (Hh < 400) { sky.style.display = 'none'; if (sPlane) sPlane.style.display = 'none'; return; }
      var W = document.documentElement.clientWidth;
      sTop = top;
      sky.style.display = 'block';
      if (sPlane) sPlane.style.display = 'block';
      sky.style.top = top + 'px';
      sky.style.height = Hh + 'px';
      sSvg.setAttribute('viewBox', '0 0 ' + W + ' ' + Hh);
      sSvg.setAttribute('width', W);
      sSvg.setAttribute('height', Hh);
      var cx = W / 2, amp = W * 0.42;
      var n = Math.max(2, Math.round(Hh / 620));
      var d = 'M ' + cx + ' 0', y = 0, side = 1;
      for (var k = 0; k < n; k++) {
        var y2 = Math.round((k + 1) * Hh / n);
        d += ' C ' + Math.round(cx + side * amp) + ' ' + Math.round(y + (y2 - y) * 0.3)
           + ', ' + Math.round(cx + side * amp) + ' ' + Math.round(y + (y2 - y) * 0.7)
           + ', ' + cx + ' ' + y2;
        y = y2;
        side = -side;
      }
      sTrack.setAttribute('d', d);
      sTrail.setAttribute('d', d);
      sL = sTrack.getTotalLength();
      sTrail.style.strokeDasharray = sL;
      sTrail.style.strokeDashoffset = sL;
      skyUpdate();
    };
    var sTick = false;
    addEventListener('scroll', function () {
      if (!sTick) { sTick = true; requestAnimationFrame(function () { sTick = false; skyUpdate(); }); }
    }, { passive: true });
    addEventListener('resize', skyBuild, { passive: true });
    addEventListener('load', skyBuild);
    if ('ResizeObserver' in window) {
      new ResizeObserver(function () { skyBuild(); }).observe(document.body);
    }
    skyBuild();
  }

  // scroll reveal
  var rv = document.querySelectorAll('[data-rv]');
  if (rv.length && 'IntersectionObserver' in window && !noMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    rv.forEach(function (el) {
      var sib = Array.prototype.filter.call(el.parentNode.children, function (c) {
        return c.hasAttribute && c.hasAttribute('data-rv');
      });
      el.style.transitionDelay = (sib.indexOf(el) % 8) * 70 + 'ms';
      el.classList.add('rv');
      io.observe(el);
    });
    // safety sweep: reveal anything already on screen (anchored loads etc.)
    var sweep = function () {
      rv.forEach(function (el) {
        if (el.classList.contains('in')) return;
        var r = el.getBoundingClientRect();
        if (r.top < (window.innerHeight || 0) && r.bottom > 0) {
          el.classList.add('in');
          io.unobserve(el);
        }
      });
    };
    addEventListener('scroll', sweep, { passive: true });
    addEventListener('load', sweep);
    setTimeout(sweep, 500);
  }

  // youtube facade: load iframe on click
  document.addEventListener('click', function (e) {
    var yt = e.target.closest('.yt');
    if (yt && !yt.querySelector('iframe')) {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube.com/embed/' + yt.dataset.id + '?autoplay=1&rel=0';
      f.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture';
      f.allowFullscreen = true;
      yt.appendChild(f);
      return;
    }

    // lightbox open
    var a = e.target.closest('.g-imgs a, figure.solo a');
    if (a) {
      e.preventDefault();
      var lb = document.querySelector('.lb');
      if (!lb) {
        lb = document.createElement('div');
        lb.className = 'lb';
        lb.innerHTML = '<button aria-label="סגירה">×</button><img alt="">';
        lb.addEventListener('click', function () { lb.classList.remove('open'); });
        document.body.appendChild(lb);
      }
      lb.querySelector('img').src = a.getAttribute('href');
      lb.classList.add('open');
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      var lb = document.querySelector('.lb.open');
      if (lb) lb.classList.remove('open');
    }
  });
})();
