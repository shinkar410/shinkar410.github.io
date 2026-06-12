// AVIATOR — minimal site interactions (no dependencies)
(function () {
  // mobile nav
  var burger = document.querySelector('.nav-burger');
  var nav = document.querySelector('.nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', nav.classList.contains('open'));
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
