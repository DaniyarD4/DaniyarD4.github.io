(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (q, el = document) => el.querySelector(q);
  const $$ = (q, el = document) => [...el.querySelectorAll(q)];

  // ---------- reveal on scroll ----------
  const rvObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
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

  // ---------- Работы: лента роликов ----------
  const reels = $('.reels');
  const rl = reels ? $$('.reel', reels) : [];
  const rInfo = reels && $('.reels-info', reels), rTabs = reels ? $$('.reels-tabs i', reels) : [];
  const rCount = reels && $('.reels-count b', reels), rSound = reels && $('.r-sound', reels);
  const rPrev = reels && $('.r-arr.prev', reels), rNext = reels && $('.r-arr.next', reels);
  let rAct = Math.min(2, rl.length - 1), rSoundOn = false, rVisible = false, rSwapT = 0;
  const rEl = (c) => rInfo && $(c, rInfo);
  const fillInfo = () => {
    const d = rl[rAct].dataset;
    rEl('.ri-big').textContent = d.big; rEl('.ri-label').textContent = d.label;
    rEl('.ri-title').textContent = d.title; rEl('.ri-text').textContent = d.text;
  };
  const rPlay = () => {
    rl.forEach((r, i) => {
      const v = $('video', r);
      if (i !== rAct || !rVisible || !r.dataset.video) { v.pause(); r.classList.remove('playing'); if (i !== rAct) r.classList.remove('paused'); return; }
      if (r.classList.contains('paused')) { v.pause(); return; }
      if (!v.getAttribute('src')) v.src = r.dataset.video;
      v.muted = !rSoundOn;
      const p = v.play();
      if (p && p.then) p.then(() => r.classList.add('playing')).catch(() => {
        v.muted = true; rSoundOn = false; syncSound();
        v.play().then(() => r.classList.add('playing')).catch(() => r.classList.add('paused'));
      });
    });
  };
  const syncSound = () => {
    if (!rSound) return;
    rSound.setAttribute('aria-pressed', String(rSoundOn));
    rSound.setAttribute('aria-label', rSoundOn ? 'Выключить звук' : 'Включить звук');
    rSound.classList.toggle('hide', !rl[rAct].dataset.video);
  };
  const rLayout = (swap) => {
    rl.forEach((r, i) => {
      const o = i - rAct;
      r.dataset.o = Math.abs(o) <= 2 ? String(o) : 'far';
      r.style.setProperty('--o', o);
      r.setAttribute('aria-hidden', o === 0 ? 'false' : 'true');
    });
    rTabs.forEach((t, i) => t.classList.toggle('on', i === rAct));
    if (rCount) rCount.textContent = String(rAct + 1).padStart(2, '0');
    if (rPrev) rPrev.disabled = rAct === 0;
    if (rNext) rNext.disabled = rAct === rl.length - 1;
    syncSound();
    if (swap && rInfo) {
      rInfo.classList.add('swap'); clearTimeout(rSwapT);
      rSwapT = setTimeout(() => { fillInfo(); rInfo.classList.remove('swap'); }, 220);
    } else fillInfo();
    rPlay();
  };
  const rGo = (i) => { i = Math.max(0, Math.min(rl.length - 1, i)); if (i === rAct) return; rAct = i; rLayout(true); };
  if (reels && rl.length) {
    // у каждого ролика: кнопка «играть», полоска прогресса с перемоткой, пауза по нажатию
    const PL = '<svg width="26" height="26" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.8v14.4c0 .8.9 1.3 1.6.9l11.3-7.2c.6-.4.6-1.3 0-1.7L8.6 3.9C7.9 3.5 7 4 7 4.8z" fill="currentColor"/></svg>';
    const togglePlay = (r) => {
      const v = $('video', r); if (!r.dataset.video) return;
      if (v.paused) { r.classList.remove('paused'); rPlay(); } else { v.pause(); r.classList.add('paused'); }
    };
    rl.forEach((r, i) => {
      const v = $('video', r);
      if (r.dataset.video) {
        r.insertAdjacentHTML('beforeend', '<span class="r-play" aria-hidden="true">' + PL + '</span><span class="r-prog" role="slider" aria-label="Перемотка" tabindex="-1"><i></i></span>');
        const bar = $('.r-prog', r), fill = $('i', bar);
        v.addEventListener('timeupdate', () => { if (v.duration) fill.style.transform = 'scaleX(' + v.currentTime / v.duration + ')'; });
        v.addEventListener('play', () => r.classList.remove('paused'));
        const seek = (e) => { const b = bar.getBoundingClientRect(); if (v.duration) v.currentTime = Math.max(0, Math.min(1, (e.clientX - b.left) / b.width)) * v.duration; };
        let drag = false;
        bar.addEventListener('pointerdown', (e) => { e.stopPropagation(); drag = true; bar.setPointerCapture(e.pointerId); seek(e); });
        bar.addEventListener('pointermove', (e) => { if (drag) seek(e); });
        bar.addEventListener('pointerup', (e) => { e.stopPropagation(); drag = false; });
        bar.addEventListener('click', (e) => e.stopPropagation());
      }
      r.addEventListener('click', () => { if (i === rAct) togglePlay(r); else rGo(i); });
    });
    rTabs.forEach((t, i) => t.addEventListener('click', () => rGo(i)));
    rPrev.addEventListener('click', () => rGo(rAct - 1));
    rNext.addEventListener('click', () => rGo(rAct + 1));
    rSound.addEventListener('click', () => { rSoundOn = !rSoundOn; syncSound(); rPlay(); });
    const stage = $('.reels-stage', reels);
    stage.tabIndex = 0;
    stage.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') rGo(rAct - 1); if (e.key === 'ArrowRight') rGo(rAct + 1); if (e.key === ' ' && e.target === stage) { e.preventDefault(); togglePlay(rl[rAct]); } });
    let sx = 0, sy = 0;
    stage.addEventListener('pointerdown', (e) => { sx = e.clientX; sy = e.clientY; });
    stage.addEventListener('pointerup', (e) => {
      const dx = e.clientX - sx, dy = e.clientY - sy;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.4) rGo(rAct + (dx < 0 ? 1 : -1));
    });
    new IntersectionObserver((en) => { rVisible = en[0].isIntersecting; rPlay(); }, { threshold: 0.35 }).observe(reels);
    rLayout(false);
  }

  // ---------- scroll-linked UI ----------
  const tl = null, bar = null;
  const chapters = tl ? $$('.chapter', tl) : [];
  const links = $$('.vnav .links a[href^="#"]');
  const linkTargets = links.map((a) => $(a.getAttribute('href')));
  const hudEls = $$('[data-hud]');
  const hud = $('.hud-label'), hudNum = $('.hud-num');
  const sb = $('.scrollbar i');
  let hudCur = '';
  const vnav = $('.vnav');
  const onScroll = () => {
    const mid = innerHeight * 0.55;
    if (vnav) vnav.classList.toggle('scrolled', scrollY > 24);
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
  };
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();

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
