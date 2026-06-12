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

  // hero carousel (crossfade + Ken Burns)
  var car = document.querySelector('.hero-car');
  if (car) {
    var slides = car.querySelectorAll('.hs');
    var dots = car.querySelectorAll('.hero-dots button');
    var cap = car.querySelector('.hero-cap');
    var i = 0, timer;
    var go = function (n) {
      slides[i].classList.remove('on');
      dots[i].classList.remove('on');
      i = (n + slides.length) % slides.length;
      if (cap) {
        cap.classList.add('fade');
        setTimeout(function () {
          cap.textContent = slides[i].dataset.cap || '';
          cap.classList.remove('fade');
        }, 300);
      }
      slides[i].classList.add('on');
      dots[i].classList.add('on');
    };
    dots.forEach(function (d, n) {
      d.addEventListener('click', function () {
        clearInterval(timer);
        go(n);
        start();
      });
    });
    var start = function () {
      if (!noMotion && slides.length > 1) {
        timer = setInterval(function () { go(i + 1); }, 5200);
      }
    };
    car.addEventListener('mouseenter', function () { clearInterval(timer); });
    car.addEventListener('mouseleave', start);
    start();
  }

  // rotating spotlight (image + text swap)
  var spot = document.querySelector('.spot');
  if (spot) {
    var sss = spot.querySelectorAll('.ss');
    var sdots = spot.querySelectorAll('.spot-dots button');
    var body = spot.querySelector('.spot-body');
    var si = 0, stimer;
    var sgo = function (n) {
      sss[si].classList.remove('on');
      sdots[si].classList.remove('on');
      si = (n + sss.length) % sss.length;
      sss[si].classList.add('on');
      sdots[si].classList.add('on');
      var d = sss[si].dataset;
      body.classList.add('swap');
      setTimeout(function () {
        body.querySelector('.kicker').textContent = d.kick;
        body.querySelector('h2').textContent = d.title;
        body.querySelector('p').textContent = d.text;
        var b = body.querySelector('.btn');
        b.textContent = d.btn;
        b.setAttribute('href', d.href);
        body.classList.remove('swap');
      }, 320);
    };
    sdots.forEach(function (d, n) {
      d.addEventListener('click', function () {
        clearInterval(stimer);
        sgo(n);
        sstart();
      });
    });
    var sstart = function () {
      if (!noMotion && sss.length > 1) {
        stimer = setInterval(function () { sgo(si + 1); }, 6500);
      }
    };
    spot.addEventListener('mouseenter', function () { clearInterval(stimer); });
    spot.addEventListener('mouseleave', sstart);
    sstart();
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
