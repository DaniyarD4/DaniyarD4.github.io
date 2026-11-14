(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (q, el = document) => el.querySelector(q);
  const $$ = (q, el = document) => [...el.querySelectorAll(q)];

  // ---------- text scramble ----------
  const GLYPHS = '▶◉◎⊙✦✧◇△▽⋆·♡';
  const scramble = (el) => {
    if (reduce || el.dataset.done) return;
    el.dataset.done = '1';
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) if (walker.currentNode.nodeValue.trim()) nodes.push({ n: walker.currentNode, t: walker.currentNode.nodeValue });
    const total = nodes.reduce((a, x) => a + x.t.length, 0);
    const dur = Math.min(1400, 500 + total * 18), t0 = performance.now();
    let idx = 0;
    nodes.forEach((x) => { x.at = [...x.t].map(() => (idx++ / total) * 0.65 + Math.random() * 0.35); });
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / dur);
      nodes.forEach((x) => {
        x.n.nodeValue = [...x.t].map((ch, i) => (ch === ' ' || ch === '\n' || p >= x.at[i]) ? ch : GLYPHS[(Math.random() * GLYPHS.length) | 0]).join('');
      });
      if (p < 1) requestAnimationFrame(tick); else nodes.forEach((x) => (x.n.nodeValue = x.t));
    };
    requestAnimationFrame(tick);
  };

  // ---------- reveal on scroll ----------
  const rvObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      if (e.target.matches('[data-scramble]')) scramble(e.target);
      $$('[data-scramble]', e.target).forEach(scramble);
      rvObs.unobserve(e.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  // ---------- count-up ----------
  const fmt = (n) => n.toLocaleString('ru-RU');
  const cntObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      cntObs.unobserve(e.target);
      if (reduce) return;
      const el = e.target, target = +el.dataset.count, t0 = performance.now(), dur = 1400;
      const tick = (t) => {
        const p = Math.min((t - t0) / dur, 1), k = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(Math.round(target * k));
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });

  // ---------- loader ----------
  const loader = $('.loader');
  const start = () => {
    $$('.rv').forEach((el) => rvObs.observe(el));
    $$('[data-count]').forEach((el) => cntObs.observe(el));
  };
  if (loader && !reduce) {
    const num = $('.loader-num', loader), bar = $('.loader-bar i', loader);
    const t0 = performance.now();
    let loaded = document.readyState === 'complete';
    addEventListener('load', () => (loaded = true));
    const tick = (now) => {
      const el = now - t0;
      const p = Math.min(1, loaded ? el / 1100 : Math.min(0.9, el / 1600));
      num.textContent = String(Math.round(p * 100)).padStart(3, '0');
      bar.style.width = p * 100 + '%';
      if (p < 1 && el < 4000) requestAnimationFrame(tick);
      else { loader.classList.add('done'); start(); }
    };
    requestAnimationFrame(tick);
  } else {
    loader && loader.classList.add('done');
    start();
  }

  // ---------- custom cursor ----------
  const cur = $('.cursor');
  if (cur && matchMedia('(pointer: fine)').matches) {
    let x = innerWidth / 2, y = innerHeight / 2, cx = x, cy = y;
    addEventListener('pointermove', (e) => { x = e.clientX; y = e.clientY; }, { passive: true });
    document.addEventListener('pointerover', (e) => cur.classList.toggle('big', !!e.target.closest('a, button')));
    const loop = () => { cx += (x - cx) * 0.2; cy += (y - cy) * 0.2; cur.style.transform = `translate(${cx}px, ${cy}px)`; requestAnimationFrame(loop); };
    loop();
  }

  // ---------- cursor glow on glass ----------
  $$('.glass').forEach((card) => {
    card.addEventListener('pointermove', (e) => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      card.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  // ---------- 3D case gallery ----------
  const gallery = $('.gallery');
  const cards = gallery ? $$('.case', gallery) : [];
  const dots = gallery ? $$('.dots i', gallery) : [];
  const counter = gallery ? $('.gallery-count', gallery) : null;
  let activeCase = -1;
  const layoutGallery = () => {
    if (!gallery) return;
    const r = gallery.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, -r.top / (r.height - innerHeight)));
    const idx = p * (cards.length - 1);
    const step = Math.min(760, innerWidth * 0.86) * (innerWidth < 720 ? 0.96 : 1.0);
    cards.forEach((c, i) => {
      const o = i - idx, a = Math.abs(o);
      c.style.transform = `translate3d(${o * step}px, 0, ${-a * 650}px) rotateY(${-o * 30}deg)`;
      c.style.opacity = String(Math.max(0, 1 - Math.max(0, a - 0.9) * 1.2));
      c.style.zIndex = String(100 - Math.round(a * 10));
      c.style.setProperty('--sx', (50 + o * 70) + '%');
      c.style.pointerEvents = a < 0.5 ? 'auto' : 'none';
    });
    const on = Math.round(idx);
    if (on !== activeCase) {
      activeCase = on;
      dots.forEach((d, i) => d.classList.toggle('on', i === on));
      if (counter) counter.textContent = String(on + 1).padStart(2, '0') + ' / ' + String(cards.length).padStart(2, '0');
      const h = $('h3', cards[on]);
      if (h) { delete h.dataset.done; scramble(h); }
    }
  };

  // ---------- scroll-linked UI ----------
  const tl = null, bar = null;
  const chapters = tl ? $$('.chapter', tl) : [];
  const links = $$('.vnav .links a[href^="#"]');
  const linkTargets = links.map((a) => $(a.getAttribute('href')));
  const hudEls = $$('[data-hud]');
  const hud = $('.hud-label'), hudNum = $('.hud-num');
  const sb = $('.scrollbar i');
  let hudCur = '';
  const onScroll = () => {
    const mid = innerHeight * 0.55;
    if (tl) {
      const r = tl.getBoundingClientRect();
      bar.style.height = Math.max(0, Math.min(r.height - 20, mid - r.top)) + 'px';
      chapters.forEach((c) => c.classList.toggle('lit', c.getBoundingClientRect().top + 50 < mid));
    }
    let cur = -1;
    linkTargets.forEach((s, i) => { if (s && s.getBoundingClientRect().top < innerHeight * 0.4) cur = i; });
    links.forEach((a, i) => a.classList.toggle('active', i === cur));
    let h = hudEls[0];
    hudEls.forEach((el) => { if (el.getBoundingClientRect().top < mid) h = el; });
    if (h && h.dataset.hud !== hudCur) {
      hudCur = h.dataset.hud;
      const [n, label] = hudCur.split('|');
      if (hudNum) { hudNum.textContent = n; hud.textContent = label; }
    }
    const max = document.documentElement.scrollHeight - innerHeight;
    if (sb) sb.style.transform = `translateY(${(scrollY / Math.max(1, max)) * 355}%)`;
    layoutGallery();
  };
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();

  // ---------- WhatsApp по нику: кнопка копирует ник и подсказывает, где его вставить ----------
  const NICK = 'daniyar2110';
  const toast = $('#toast');
  let toastT;
  const show = (html) => { toast.innerHTML = html; toast.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(() => toast.classList.remove('show'), 6000); };
  const copy = (text) => {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    const t = document.createElement('textarea'); t.value = text; t.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(t); t.select();
    try { document.execCommand('copy'); } catch (e) { /* старый браузер: ник всё равно покажем */ }
    document.body.removeChild(t);
    return Promise.resolve();
  };
  $$('[data-wa]').forEach((btn) => btn.addEventListener('click', (e) => {
    e.preventDefault();
    const fmt = btn.dataset.wa, tail = fmt ? ' Спросите про формат «' + fmt + '».' : '';
    copy(NICK).then(
      () => show('Ник <b>@' + NICK + '</b> скопирован. Откройте WhatsApp и вставьте его в поиск.' + tail),
      () => show('Мой WhatsApp: <b>@' + NICK + '</b>. Найдите этот ник через поиск в WhatsApp.' + tail));
  }));

  // ---------- плеер роликов из кейсов: видео грузится только по нажатию ----------
  const player = $('.player'), video = player && $('video', player), pnav = player && $('.player-nav', player);
  let list = [];
  const play = (k) => {
    video.src = list[k].src; video.poster = list[k].poster || '';
    $$('button', pnav).forEach((b, i) => b.classList.toggle('on', i === k));
    const p = video.play(); if (p && p.catch) p.catch(() => {});
  };
  const openPlayer = (btn) => {
    const posters = (btn.dataset.posters || '').split('|');
    list = btn.dataset.videos.split('|').map((v, i) => ({ src: v, poster: posters[i] }));
    pnav.innerHTML = list.length > 1 ? list.map((_, i) => '<button type="button" aria-label="Ролик ' + (i + 1) + '">' + (i + 1) + '</button>').join('') : '';
    $$('button', pnav).forEach((b, i) => b.addEventListener('click', () => play(i)));
    player.classList.add('open'); document.body.style.overflow = 'hidden';
    play(0); $('.player-close', player).focus();
  };
  const closePlayer = () => { video.pause(); video.removeAttribute('src'); video.load(); player.classList.remove('open'); document.body.style.overflow = ''; };
  if (player) {
    $$('[data-videos]').forEach((b) => b.addEventListener('click', () => openPlayer(b)));
    $('.player-close', player).addEventListener('click', closePlayer);
    player.addEventListener('click', (e) => { if (e.target === player) closePlayer(); });
    addEventListener('keydown', (e) => { if (e.key === 'Escape' && player.classList.contains('open')) closePlayer(); });
  }
})();
