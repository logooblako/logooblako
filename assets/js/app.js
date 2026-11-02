/* Логооблако — интерактив без библиотек */
(function () {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const url = (root, p) => !p ? "" : /^(https?:|data:)/.test(p) ? p : root + p.replace(/^\//, "");
  const star = el => { el.textContent += "⭐"; el.classList.remove("pop"); void el.offsetWidth; el.classList.add("pop"); };

  /* вкладки */
  $$("[data-tabs]").forEach(bar => {
    const scope = bar.parentElement;
    const show = id => {
      $$(".tab", bar).forEach(t => t.classList.toggle("on", t.dataset.tab === id));
      $$("[data-panel]", scope).forEach(p => p.classList.toggle("on", p.dataset.panel === id));
    };
    $$(".tab", bar).forEach(t => t.addEventListener("click", () => { show(t.dataset.tab); if (bar.hasAttribute("data-hash")) history.replaceState(null, "", "#" + t.dataset.tab); }));
    if (bar.hasAttribute("data-hash") && location.hash && $(`[data-tab="${location.hash.slice(1)}"]`, bar)) show(location.hash.slice(1));
  });

  /* отметка картинок */
  $$("[data-toggle]").forEach(el => el.addEventListener("click", () => el.classList.toggle("done")));

  /* «Назови картинку» */
  $$("[data-namegame]").forEach(g => {
    const root = g.dataset.root, items = shuffle(JSON.parse(g.dataset.namegame)); let i = 0;
    const img = $(".stage img", g), word = $(".word", g), stars = $(".stars", g);
    const show = () => { const it = items[i % items.length]; img.src = url(root, it.p); img.alt = it.w; word.textContent = ""; };
    $("[data-hint]", g).onclick = () => { word.textContent = items[i % items.length].w; };
    $("[data-ok]", g).onclick = () => { star(stars); i++; show(); };
    $("[data-next]", g).onclick = () => { i++; show(); };
    show();
  });

  /* «Разложи по домикам» */
  $$("[data-sortgame]").forEach(g => {
    const root = g.dataset.root; let items = shuffle(JSON.parse(g.dataset.sortgame)); let i = 0;
    const img = $(".stage img", g), word = $(".word", g), stars = $(".stars", g);
    const show = () => { if (i >= items.length) { word.textContent = "Молодец! Все картинки в домиках 🎉"; img.style.visibility = "hidden"; return; } const it = items[i]; img.style.visibility = ""; img.src = url(root, it.p); img.alt = it.w; word.textContent = it.w; };
    $$("[data-house]", g).forEach(b => b.onclick = () => {
      if (i >= items.length) { items = shuffle(items); i = 0; stars.textContent = ""; show(); return; }
      if (b.dataset.house === items[i].h) { star(stars); i++; show(); }
      else { b.classList.remove("shake"); void b.offsetWidth; b.classList.add("shake"); word.textContent = items[i].w + " — послушай ещё раз"; }
    });
    show();
  });

  /* Конструктор игр: проигрыватель */
  function play(box, G, root) {
    const cards = (G.cards || []).filter(c => c.text || c.pic);
    if (!cards.length) { box.innerHTML = '<div class="word muted">Добавьте карточки — и игра появится здесь</div>'; return; }
    const aud = c => c && c.audio ? ` <button class="mini aud" data-audio="${url(root, c.audio)}" title="Послушать">🔊</button>` : "";
    const pic = (p, size = 120) => p ? `<img src="${url(root, p)}" alt="" style="width:${size}px;height:${size}px;object-fit:contain">` : "";
    const esc = s => String(s || "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const T = {
      quiz() {
        let i = 0, score = 0; const qs = shuffle(cards);
        const draw = () => {
          if (i >= qs.length) { box.innerHTML = `<div class="word">Готово! Верно: ${score} из ${qs.length} 🎉</div><button class="btn main" id="again">Ещё раз</button>`; $("#again").onclick = () => T.quiz(); return; }
          const q = qs[i]; const opts = shuffle([q.back, ...String(q.options || "").split(",").map(s => s.trim()).filter(Boolean)]);
          box.innerHTML = `<div class="stars">${"⭐".repeat(score)}</div><div class="stage">${pic(q.pic, 150)}</div><div class="word">${esc(q.text)}${aud(q)}</div>
            <div class="btns" style="justify-content:center">${opts.map(o => `<button class="btn soft" data-o="${esc(o)}">${esc(o)}</button>`).join("")}</div>`;
          $$("[data-o]", box).forEach(b => b.onclick = () => { if (b.dataset.o === q.back) { score++; b.style.background = "#d9f5ee"; } else { b.classList.add("shake"); b.style.background = "#ffe1d6"; } setTimeout(() => { i++; draw(); }, 700); });
        }; draw();
      },
      pairs() {
        const deck = shuffle(cards.flatMap((c, k) => [{ k, t: c.text, p: c.pic, a: c.audio }, { k, t: c.back || c.text, p: c.back ? (c.back_pic || "") : c.pic, a: c.audio }]));
        let open = [], done = 0, moves = 0;
        box.innerHTML = `<div class="stars"></div><div class="pics" id="deck"></div>`;
        const D = $("#deck", box);
        deck.forEach((c, n) => { const el = document.createElement("div"); el.className = "pic"; el.style.minHeight = "130px"; el.dataset.n = n; el.innerHTML = `<div style="font-size:48px;line-height:110px">❓</div>`; D.appendChild(el);
          el.onclick = () => { if (open.length === 2 || el.classList.contains("done") || open.includes(el)) return; el.innerHTML = pic(c.p, 70) + `<b>${esc(c.t)}</b>`; if (c.a) new Audio(url(root, c.a)).play().catch(() => {}); open.push(el);
            if (open.length === 2) { moves++; const [a, b] = open; if (deck[a.dataset.n].k === deck[b.dataset.n].k) { a.classList.add("done"); b.classList.add("done"); open = []; done++; star($(".stars", box)); if (done === cards.length) setTimeout(() => { box.insertAdjacentHTML("beforeend", `<div class="word">Все пары найдены за ${moves} ходов! <button class="btn main" id="again">Ещё раз</button></div>`); $("#again").onclick = () => T.pairs(); }, 400); }
              else setTimeout(() => { [a, b].forEach(x => x.innerHTML = `<div style="font-size:48px;line-height:110px">❓</div>`); open = []; }, 900); } }; });
      },
      sort() {
        const groups = String(G.groups || "").split(",").map(s => s.trim()).filter(Boolean); let items = shuffle(cards), i = 0;
        const colors = ["var(--mint)", "var(--coral)", "var(--sky)", "var(--sun)"];
        box.innerHTML = `<div class="stars"></div><div class="stage" id="st"></div><div class="word" id="wd"></div><div class="houses" style="grid-template-columns:repeat(${Math.min(groups.length, 4)},1fr)">${groups.map((g, n) => `<button class="house" style="background:${colors[n % 4]};font-size:24px" data-g="${esc(g)}">${esc(g)}</button>`).join("")}</div>`;
        const draw = () => { if (i >= items.length) { $("#st", box).innerHTML = "🎉"; $("#wd", box).textContent = "Всё разложено!"; return; } $("#st", box).innerHTML = pic(items[i].pic, 150); $("#wd", box).innerHTML = esc(items[i].text) + aud(items[i]); };
        $$("[data-g]", box).forEach(b => b.onclick = () => { if (i >= items.length) { items = shuffle(cards); i = 0; $(".stars", box).textContent = ""; draw(); return; } if (b.dataset.g === (items[i].group || "").trim()) { star($(".stars", box)); i++; draw(); } else { b.classList.remove("shake"); void b.offsetWidth; b.classList.add("shake"); } });
        draw();
      },
      wheel() {
        const n = cards.length, colors = ["#ffb4a2", "#9fe3d3", "#a9cdfa", "#ffe08a", "#c9bfff", "#ffc2d6"];
        const seg = 360 / n; let rot = 0;
        const grad = cards.map((c, k) => `${colors[k % colors.length]} ${k * seg}deg ${(k + 1) * seg}deg`).join(",");
        box.innerHTML = `<div style="position:relative;width:min(340px,80vw);aspect-ratio:1;margin:10px auto">
          <div id="wh" style="width:100%;height:100%;border-radius:50%;background:conic-gradient(${grad});border:8px solid #fff;box-shadow:var(--shadow);transition:transform 3.5s cubic-bezier(.17,.67,.2,1)"></div>
          <div style="position:absolute;top:-6px;left:50%;transform:translateX(-50%);font-size:34px">🔻</div></div>
          <button class="btn main" id="spin">Крутить!</button><div class="stage" id="res" style="min-height:180px"></div>`;
        $("#spin", box).onclick = () => { const k = Math.floor(Math.random() * n); rot += 360 * 5 + (360 - (k * seg + seg / 2)) - (rot % 360); $("#wh", box).style.transform = `rotate(${rot}deg)`; $("#res", box).innerHTML = "";
          setTimeout(() => { const c = cards[k]; $("#res", box).innerHTML = `<div>${pic(c.pic, 140)}<div class="word">${esc(c.text)}${aud(c)}</div>${c.back ? `<p>${esc(c.back)}</p>` : ""}</div>`; }, 3600); };
      },
      flip() {
        box.innerHTML = `<div class="pics">${cards.map((c, k) => `<div class="pic" data-k="${k}" style="min-height:170px">${pic(c.pic, 80)}<b>${esc(c.text)}</b>${aud(c)}</div>`).join("")}</div>`;
        $$("[data-k]", box).forEach(el => { let back = false; el.onclick = () => { const c = cards[el.dataset.k]; back = !back; el.classList.toggle("done", back); el.innerHTML = back ? `<div style="font-size:20px;font-weight:900;padding:30px 4px">${esc(c.back || "—")}</div>` : pic(c.pic, 80) + `<b>${esc(c.text)}</b>` + aud(c); }; });
      },
      slides() {
        let i = 0;
        const draw = () => { const c = cards[i]; box.innerHTML = `<div class="muted">${i + 1} / ${cards.length}</div><div class="stage" style="min-height:260px">${pic(c.pic, 200)}</div><h2>${esc(c.text)}${aud(c)}</h2><p style="font-size:20px">${esc(c.back)}</p>
          <div class="btns" style="justify-content:center"><button class="btn soft" id="pv">← Назад</button><button class="btn main" id="nx">Дальше →</button><button class="btn soft" id="fs">На весь экран</button></div>`;
          $("#pv", box).onclick = () => { i = (i - 1 + cards.length) % cards.length; draw(); }; $("#nx", box).onclick = () => { i = (i + 1) % cards.length; draw(); };
          $("#fs", box).onclick = () => box.requestFullscreen && box.requestFullscreen(); };
        if (box._kd) document.removeEventListener("keydown", box._kd);
        box._kd = e => { if (!document.body.contains(box)) return; if (e.key === "ArrowRight") { i = (i + 1) % cards.length; draw(); } if (e.key === "ArrowLeft") { i = (i - 1 + cards.length) % cards.length; draw(); } };
        document.addEventListener("keydown", box._kd);
        draw();
      }
    };
    (T[G.template] || T.flip)();
  }
  window.LogoPlay = play;
  document.addEventListener("click", e => { const b = e.target.closest("[data-audio]"); if (!b) return; e.stopPropagation(); e.preventDefault(); new Audio(b.dataset.audio).play().catch(() => {}); }, true);
  const box = $("#game-player");
  if (box) {
    let G = JSON.parse(box.dataset.game);
    const m = location.hash.match(/^#g=(.+)$/);
    if (box.dataset.shared && m) { try { G = JSON.parse(decodeURIComponent(escape(atob(m[1])))); const h = $("h1"); if (h && G.title) h.textContent = G.title; } catch (e) {} }
    play(box, G, box.dataset.root);
  }
})();

/* поделиться */
(function(){
  const link = location.href.split("#")[0], title = document.title;
  document.querySelectorAll("[data-share-to]").forEach(a => {
    const e = encodeURIComponent(link), t = encodeURIComponent(title);
    a.href = {tg:`https://t.me/share/url?url=${e}&text=${t}`, vk:`https://vk.com/share.php?url=${e}`, wa:`https://wa.me/?text=${t}%20${e}`}[a.dataset.shareTo];
  });
  const b = document.querySelector("[data-share]"), note = document.querySelector("[data-copied]");
  if (b) b.onclick = async () => {
    if (navigator.share) { try { await navigator.share({title, url: link}); } catch(e){} return; }
    try { await navigator.clipboard.writeText(link); note.textContent = "Ссылка скопирована"; } catch(e) { note.textContent = link; }
  };
})();
