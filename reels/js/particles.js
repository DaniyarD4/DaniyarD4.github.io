// Облако частиц по прокрутке: одно облако перестраивается из фигуры в фигуру,
// по фигуре на раздел страницы (см. data-stage в index.html). Основа — about-me/js/particles.js.
(() => {
  const canvas = document.getElementById('gl');
  const gl = canvas && (canvas.getContext('webgl', { antialias: false, alpha: false, powerPreference: 'high-performance' }));
  if (!gl) { document.documentElement.classList.add('no-gl'); return; }

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const mobile = matchMedia('(max-width: 760px)').matches;
  const N = mobile ? 7000 : 14000;
  const TAU = Math.PI * 2;

  // ---------- per-particle randoms ----------
  const rnd = new Float32Array(N * 4);
  const dir = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    for (let k = 0; k < 4; k++) rnd[i * 4 + k] = Math.random();
    const u = Math.random() * 2 - 1, t = Math.random() * TAU, s = Math.sqrt(1 - u * u);
    dir[i * 3] = s * Math.cos(t); dir[i * 3 + 1] = u; dir[i * 3 + 2] = s * Math.sin(t);
  }
  const gauss = () => { let u = 0, v = 0; while (!u) u = Math.random(); while (!v) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v); };

  // ---------- shapes ----------
  const build = (fn) => { const a = new Float32Array(N * 3); for (let i = 0; i < N; i++) fn(i, a, i * 3); return a; };

  // Фигуры по разделам Reels-страницы (data-stage в index.html):
  // 0 объектив · 1–4 звёздное небо · 5 портрет

  // 0 — объектив: насечка, кольца оправы, лепестки диафрагмы (вращаются), стекло с бликами
  const BLADES = 7, R_IN = 1.85;
  const lensKind = new Uint8Array(N), lensA = new Float32Array(N), lensB = new Float32Array(N);
  const lens = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    const k = rnd[i * 4 + 2], o = i * 3;
    if (k < 0.16) { // насечка фокусного кольца
      const t = Math.floor(Math.random() * 96) / 96 * TAU + gauss() * 0.004, r = 2.42 + Math.random() * 0.2;
      lens[o] = Math.cos(t) * r; lens[o + 1] = Math.sin(t) * r; lens[o + 2] = gauss() * 0.03; lensKind[i] = 0;
    } else if (k < 0.34) { // тонкие кольца оправы
      const R = [2.25, 2.12, 1.9][Math.floor(Math.random() * 3)], t = Math.random() * TAU;
      lens[o] = Math.cos(t) * R + gauss() * 0.008; lens[o + 1] = Math.sin(t) * R + gauss() * 0.008; lens[o + 2] = gauss() * 0.02; lensKind[i] = 0;
    } else if (k < 0.64) { // кромки лепестков диафрагмы
      lensKind[i] = 1; lensA[i] = Math.floor(Math.random() * BLADES); lensB[i] = Math.random();
    } else if (k < 0.74) { // тело лепестков: редкая заливка
      lensKind[i] = 2; lensA[i] = Math.random() * TAU; lensB[i] = Math.random();
    } else if (k < 0.88) { // стекло в отверстии
      const t = Math.random() * TAU, r = Math.sqrt(Math.random()) * 0.62;
      lens[o] = Math.cos(t) * r; lens[o + 1] = Math.sin(t) * r; lens[o + 2] = Math.sqrt(Math.max(0, 0.4 - r * r)) * 0.6; lensKind[i] = 0;
      if (Math.random() < 0.35) { const tt = 2.1 + Math.random() * 0.9, rr = 0.36 + gauss() * 0.02; lens[o] = Math.cos(tt) * rr; lens[o + 1] = Math.sin(tt) * rr; lens[o + 2] = 0.35; }
    } else { // пыль вокруг
      const t = Math.random() * TAU, r = 2.7 + Math.abs(gauss()) * 0.9;
      lens[o] = Math.cos(t) * r; lens[o + 1] = Math.sin(t) * r; lens[o + 2] = gauss() * 0.25; lensKind[i] = 0;
    }
  }
  const updateLens = (time) => {
    const rot = time * 0.12, open = 0.66 + Math.sin(time * 0.45) * 0.1;
    for (let i = 0; i < N; i++) {
      const kd = lensKind[i]; if (!kd) continue;
      const o = i * 3;
      if (kd === 1) { // кромка лепестка: от вершины отверстия по касательной к оправе
        const a = lensA[i] / BLADES * TAU + rot, u = lensB[i];
        const x0 = Math.cos(a) * open, y0 = Math.sin(a) * open, d = a + 1.95;
        const len = R_IN * 1.15 * u;
        let x = x0 + Math.cos(d) * len, y = y0 + Math.sin(d) * len;
        const r = Math.hypot(x, y); if (r > R_IN) { x *= R_IN / r; y *= R_IN / r; }
        lens[o] = x + gauss() * 0.01; lens[o + 1] = y + gauss() * 0.01; lens[o + 2] = 0.05;
      } else { // заливка между отверстием и оправой
        const t = lensA[i] + rot * 0.5, r = open + (R_IN - open) * Math.sqrt(lensB[i]);
        lens[o] = Math.cos(t) * r; lens[o + 1] = Math.sin(t) * r; lens[o + 2] = 0.02;
      }
    }
  };
  updateLens(0);

  const field = build((i, a, o) => {
    if (rnd[i * 4 + 2] < 0.35) { // milky way band
      const x = (Math.random() - 0.5) * 22; a[o] = x; a[o + 1] = x * 0.32 + gauss() * 0.7; a[o + 2] = -4 - Math.random() * 6; return;
    }
    a[o] = (Math.random() - 0.5) * 20; a[o + 1] = (Math.random() - 0.5) * 12; a[o + 2] = -Math.random() * 12 + 2;
  });

  const portrait = build((i, a, o) => { // placeholder until the photo is sampled
    const t = Math.random() * TAU, r = Math.sqrt(Math.random()) * 1.8;
    a[o] = Math.cos(t) * r; a[o + 1] = Math.sin(t) * r; a[o + 2] = gauss() * 0.1;
  });

  // Сдержанно: объектив на первом экране и портрет в финале, между ними тихое звёздное небо
  const shapes = [lens, field, field, field, field, portrait];
  // per-stage look: [offsetX desktop, offsetY desktop, offsetY mobile, dim, moonlight share, spin speed, rotation allowed]
  const LOOK = [
    [2.65, 0.25, 2.25, 1.0, 0.15, 0.0, 0],
    [0, 0, 0, 0.3, 0.6, 0.012, 1],
    [0, 0, 0, 0.3, 0.6, 0.012, 1],
    [0, 0, 0, 0.3, 0.6, 0.012, 1],
    [0, 0, 0, 0.3, 0.6, 0.012, 1],
    [2.3, 0, 2.05, 1.0, 0.0, 0.0, 0],
  ];
  const lastStage = shapes.length - 1;

  // ---------- GL setup ----------
  const vs = `
    attribute vec3 aPos; attribute vec4 aRnd; attribute vec3 aPhoto;
    uniform mat4 uProj; uniform float uTime, uPixel, uSize, uHolo, uPhoto, uRot, uTiltX, uTiltY, uScale;
    uniform vec3 uOffset;
    uniform vec3 uC1, uC2, uC3, uC4, uS1, uS2, uS3, uTint;
    varying vec3 vCol; varying float vA;
    vec3 mainTone(float r) { return r < .5 ? uC1 : r < .75 ? uC2 : r < .9 ? uC3 : uC4; }
    vec3 moonTone(float r) { return r < .55 ? uS1 : r < .85 ? uS2 : uS3; }
    void main() {
      vec3 p = aPos * uScale;
      float t = uTime;
      p += .035 * vec3(sin(t*.7 + aRnd.x*40.), cos(t*.6 + aRnd.y*40.), sin(t*.5 + aRnd.z*40.));
      float c = cos(uRot + uTiltX), s = sin(uRot + uTiltX);
      p = vec3(c*p.x + s*p.z, p.y, -s*p.x + c*p.z);
      float c2 = cos(uTiltY), s2 = sin(uTiltY);
      p = vec3(p.x, c2*p.y - s2*p.z, s2*p.y + c2*p.z);
      p += uOffset;
      vec4 mv = vec4(p + vec3(0., 0., -7.5), 1.);
      gl_Position = uProj * mv;
      float sz = uSize * (.45 + aRnd.w * aRnd.w * 1.6);
      gl_PointSize = clamp(sz * uPixel / -mv.z, 1., 40.);
      vec3 col = aRnd.y < uHolo ? moonTone(aRnd.z) : mainTone(aRnd.z);
      vCol = mix(col, aPhoto * uTint, uPhoto);
      vA = (.5 + .5 * sin(t * (1. + aRnd.x * 2.) + aRnd.y * 60.)) * .6 + .4;
      vA *= smoothstep(-22., -4., mv.z);
    }`;
  const fs = `
    precision mediump float;
    uniform float uDim;
    varying vec3 vCol; varying float vA;
    void main() {
      float d = length(gl_PointCoord - .5);
      float a = smoothstep(.5, 0., d); a *= a;
      gl_FragColor = vec4(vCol * a * vA * uDim, 1.);
    }`;
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
  let prog;
  try {
    prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, fs));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  } catch (e) { console.warn(e); document.documentElement.classList.add('no-gl'); return; }
  gl.useProgram(prog);

  const pos = new Float32Array(N * 3);
  const photo = new Float32Array(N * 3).fill(0.8);
  const buf = (data, name, size, usage) => {
    const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, data, usage || gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, name); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
    return b;
  };
  const posBuf = buf(pos, 'aPos', 3, gl.DYNAMIC_DRAW);
  buf(rnd, 'aRnd', 4);
  const photoBuf = buf(photo, 'aPhoto', 3);
  const U = {};
  ['uProj', 'uTime', 'uPixel', 'uSize', 'uHolo', 'uPhoto', 'uRot', 'uTiltX', 'uTiltY', 'uScale', 'uOffset', 'uDim', 'uC1', 'uC2', 'uC3', 'uC4', 'uS1', 'uS2', 'uS3', 'uTint'].forEach((n) => (U[n] = gl.getUniformLocation(prog, n)));
  const applyTheme = () => {
    const cs = getComputedStyle(document.documentElement);
    const v = (name, fb) => { const p = cs.getPropertyValue(name).trim().split(/\s+/).map(Number); return p.length === 3 && p.every((x) => !isNaN(x)) ? p : fb; };
    [['uC1', '--pc1'], ['uC2', '--pc2'], ['uC3', '--pc3'], ['uC4', '--pc4'], ['uS1', '--ps1'], ['uS2', '--ps2'], ['uS3', '--ps3'], ['uTint', '--photo-tint']]
      .forEach(([u, c]) => gl.uniform3fv(U[u], v(c, [1, 1, 1])));
    const bg = v('--ink-rgb', null) || cs.getPropertyValue('--ink-rgb').split(',').map((x) => +x);
    gl.clearColor(bg[0] / 255, bg[1] / 255, bg[2] / 255, 1);
  };
  applyTheme();
  new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  gl.disable(gl.DEPTH_TEST);
  gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);

  let W = 0, H = 0, aspect = 1;
  const FOV = 50 * Math.PI / 180;
  const resize = () => {
    const dpr = Math.min(window.devicePixelRatio || 1, mobile ? 1.5 : 1.75);
    W = canvas.width = Math.round(innerWidth * dpr); H = canvas.height = Math.round(innerHeight * dpr);
    gl.viewport(0, 0, W, H);
    aspect = W / H;
    const f = 1 / Math.tan(FOV / 2), nr = 0.1, fr = 100;
    gl.uniformMatrix4fv(U.uProj, false, new Float32Array([f / aspect, 0, 0, 0, 0, f, 0, 0, 0, 0, (fr + nr) / (nr - fr), -1, 0, 0, 2 * fr * nr / (nr - fr), 0]));
    gl.uniform1f(U.uPixel, H / (2 * Math.tan(FOV / 2)));
    gl.uniform1f(U.uSize, mobile ? 0.05 : 0.042);
  };
  resize(); addEventListener('resize', resize);

  // ---------- portrait sampling ----------
  const img = new Image();
  img.onload = () => {
    try {
      const S = 140, c = document.createElement('canvas'); c.width = c.height = S;
      const x2 = c.getContext('2d', { willReadFrequently: true }); x2.drawImage(img, 0, 0, S, S);
      const d = x2.getImageData(0, 0, S, S).data;
      let n = 0, guard = 0;
      while (n < N && guard++ < N * 80) {
        const x = Math.random() * S | 0, y = Math.random() * S | 0;
        const dx = x / S - 0.5, dy = y / S - 0.47;
        if (dx * dx * 1.1 + dy * dy > 0.2) continue;
        const k = (y * S + x) * 4, r = d[k] / 255, g = d[k + 1] / 255, b = d[k + 2] / 255;
        const lum = 0.3 * r + 0.59 * g + 0.11 * b;
        if (Math.random() > Math.pow(lum, 1.1) * 1.6 + 0.015) continue;
        portrait[n * 3] = dx * 4.4; portrait[n * 3 + 1] = -dy * 4.4; portrait[n * 3 + 2] = lum * 0.6 + gauss() * 0.02;
        photo[n * 3] = Math.min(1, r * 1.25); photo[n * 3 + 1] = Math.min(1, g * 1.25); photo[n * 3 + 2] = Math.min(1, b * 1.25);
        n++;
      }
      gl.bindBuffer(gl.ARRAY_BUFFER, photoBuf); gl.bufferData(gl.ARRAY_BUFFER, photo, gl.STATIC_DRAW);
      lastS = -1; // force re-morph
    } catch (e) { /* tainted canvas (file://) — keep the placeholder disc */ }
  };
  img.src = canvas.dataset.portrait || 'img/portrait.jpg';

  // ---------- scroll → stage ----------
  const anchors = [...document.querySelectorAll('[data-stage]')];
  const targetStage = () => {
    const mid = innerHeight * 0.5;
    for (let i = 0; i < anchors.length; i++) {
      const r = anchors[i].getBoundingClientRect();
      if (r.bottom < mid && i < anchors.length - 1) continue;
      const st = +anchors[i].dataset.stage;
      const prev = i > 0 ? +anchors[i - 1].dataset.stage : st;
      // blend in during the first 35% of a viewport after the section top crosses mid
      const p = Math.min(1, Math.max(0, (mid - r.top) / (innerHeight * 0.35)));
      return r.top > mid ? prev : prev + (st - prev) * p;
    }
    return 0;
  };

  let s = 1.0, lastS = -1; // start from the next shape and assemble into the hero lens
  const anchor = document.querySelector('[data-gl-anchor]');
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  addEventListener('pointermove', (e) => { mouse.tx = e.clientX / innerWidth - 0.5; mouse.ty = e.clientY / innerHeight - 0.5; }, { passive: true });

  const ease = (x) => x * x * (3 - 2 * x);
  const morph = () => {
    const a = Math.min(Math.floor(s), lastStage), b = Math.min(a + 1, lastStage), f = s - a;
    const A = shapes[a], B = shapes[b];
    for (let i = 0; i < N; i++) {
      const delay = rnd[i * 4 + 3] * 0.35;
      const fi = ease(Math.min(1, Math.max(0, (f - delay) / 0.65)));
      const burst = Math.sin(fi * Math.PI) * (0.6 + rnd[i * 4] * 1.6);
      const o = i * 3;
      pos[o] = A[o] + (B[o] - A[o]) * fi + dir[o] * burst;
      pos[o + 1] = A[o + 1] + (B[o + 1] - A[o + 1]) * fi + dir[o + 1] * burst;
      pos[o + 2] = A[o + 2] + (B[o + 2] - A[o + 2]) * fi + dir[o + 2] * burst;
    }
    gl.bindBuffer(gl.ARRAY_BUFFER, posBuf); gl.bufferSubData(gl.ARRAY_BUFFER, 0, pos);
  };
  const lookAt = (k) => {
    const a = Math.min(Math.floor(s), lastStage), b = Math.min(a + 1, lastStage), f = ease(s - a);
    return LOOK[a][k] + (LOOK[b][k] - LOOK[a][k]) * f;
  };

  let rot = 0, last = performance.now(), visible = true;
  document.addEventListener('visibilitychange', () => { visible = !document.hidden; if (visible) { last = performance.now(); requestAnimationFrame(frame); } });

  function frame(now) {
    if (!visible) return;
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    const tgt = targetStage();
    s += (tgt - s) * (reduce ? 1 : Math.min(1, dt * 2.6));
    if (Math.abs(s - tgt) < 1e-4) s = tgt;
    const orbiting = s < 1 && !reduce;
    if (orbiting) updateLens(now / 1000);
    if (orbiting || Math.abs(s - lastS) > 1e-5) { morph(); lastS = s; }

    mouse.x += (mouse.tx - mouse.x) * 0.05; mouse.y += (mouse.ty - mouse.y) * 0.05;
    if (!reduce) rot += dt * lookAt(5);
    const narrow = aspect < 0.9;
    let ox = narrow ? 0 : lookAt(0) * Math.min(1, aspect / 1.6);
    let oy = narrow ? lookAt(2) : lookAt(1);
    // вариант с телефоном: объектив встаёт ровно за телефоном и уезжает вместе с ним при прокрутке
    if (anchor && anchor.offsetParent && s < 1) {
      const r = anchor.getBoundingClientRect(), hh = Math.tan(FOV / 2) * 7.5;
      const ax = ((r.left + r.width / 2) / innerWidth - 0.5) * 2 * hh * aspect;
      const ay = (0.5 - (r.top + r.height / 2) / innerHeight) * 2 * hh;
      const k = ease(Math.min(1, s));
      ox = ax + (ox - ax) * k; oy = ay + (oy - ay) * k;
    }
    gl.uniform1f(U.uTime, reduce ? 0 : now / 1000);
    const pw = Math.max(0, s - (lastStage - 1));
    let r = rot % TAU; if (r > Math.PI) r -= TAU;
    gl.uniform1f(U.uRot, r * lookAt(6));
    gl.uniform1f(U.uTiltX, mouse.x * (0.5 - pw * 0.3));
    gl.uniform1f(U.uTiltY, mouse.y * 0.3);
    gl.uniform3f(U.uOffset, ox, oy, 0);
    const hero = Math.max(0, 1 - s); // телефоны: объективу нужен масштаб поменьше и точки мельче
    gl.uniform1f(U.uScale, narrow ? 0.62 * (1 - 0.15 * hero) : 1);
    gl.uniform1f(U.uSize, (mobile ? 0.05 : 0.042) * (narrow ? 1 - 0.45 * hero : 1));
    gl.uniform1f(U.uDim, lookAt(3) * (narrow ? 0.85 : 1));
    gl.uniform1f(U.uHolo, lookAt(4));
    gl.uniform1f(U.uPhoto, pw);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.drawArrays(gl.POINTS, 0, N);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
