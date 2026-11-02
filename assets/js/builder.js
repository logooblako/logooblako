/* Логооблако — конструктор игр (всё хранится в браузере) */
(function () {
  const $ = s => document.querySelector(s);
  const KEY = "logo-my-games";
  const HINTS = {
    quiz: { t: "Вопрос", b: "Правильный ответ", o: true, g: false, help: "Каждая карточка — вопрос с картинкой. Впишите правильный ответ и неверные варианты через запятую." },
    pairs: { t: "Слово", b: "Пара (необязательно)", o: false, g: false, help: "Если «пару» не заполнять, ребёнок ищет две одинаковые картинки." },
    sort: { t: "Слово", b: "", o: false, g: true, help: "Впишите группы через запятую (например: С, Ш) и у каждой карточки укажите её группу." },
    wheel: { t: "Текст", b: "Подпись (необязательно)", o: false, g: false, help: "Колесо выбирает случайную карточку: слово, скороговорку, задание." },
    flip: { t: "Лицевая сторона", b: "Оборот", o: false, g: false, help: "Ребёнок называет картинку, потом переворачивает карточку." },
    slides: { t: "Заголовок слайда", b: "Текст слайда", o: false, g: false, help: "Презентация листается кнопками или стрелками на клавиатуре." }
  };
  let G = blank(), editing = null, pickFor = null;
  function blank() { return { title: "", template: "quiz", groups: "", cards: [card(), card(), card()] }; }
  function card() { return { text: "", pic: "", back: "", group: "", options: "", audio: "" }; }
  const esc = s => String(s || "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const src = p => !p ? "" : /^(data:|https?:)/.test(p) ? p : ROOT + p.replace(/^\//, "");
  const msg = t => { $("#b-msg").textContent = t; };
  const mine = () => { try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return []; } };
  const setMine = a => { try { localStorage.setItem(KEY, JSON.stringify(a)); return true; } catch (e) { msg("Не удалось сохранить: в браузере мало места (уменьшите число своих фото)."); return false; } };

  function drawForm() {
    const h = HINTS[G.template];
    $("#b-title").value = G.title; $("#b-tpl").value = G.template; $("#b-groups").value = G.groups;
    $("#b-hint").textContent = h.help; $("#b-groups-wrap").style.display = h.g ? "" : "none";
    $("#b-cards").innerHTML = G.cards.map((c, i) => `
      <div class="bcard" data-i="${i}">
        <button class="bpic" data-pick="${i}" title="Выбрать картинку">${c.pic ? `<img src="${esc(src(c.pic))}" alt="">` : "＋ картинка"}</button>
        <div class="bfields">
          <input class="inp" data-f="text" placeholder="${h.t}" value="${esc(c.text)}">
          ${h.b ? `<input class="inp" data-f="back" placeholder="${h.b}" value="${esc(c.back)}">` : ""}
          ${h.g ? `<input class="inp" data-f="group" placeholder="Группа" value="${esc(c.group)}">` : ""}
          ${h.o ? `<input class="inp" data-f="options" placeholder="Неверные ответы через запятую" value="${esc(c.options)}">` : ""}
        </div>
        <div class="bact"><label class="mini" title="Загрузить аудио" style="cursor:pointer">${c.audio ? "🔊" : "🎵"}<input type="file" accept="audio/*" data-aud="${i}" hidden></label>${c.audio ? `<button class="mini" data-noaud="${i}" title="Убрать аудио">🔇</button>` : ""}<button class="mini" data-up="${i}" title="Выше">↑</button><button class="mini" data-del="${i}" title="Удалить">✕</button></div>
      </div>`).join("");
    preview();
  }
  let tmr; function preview() { clearTimeout(tmr); tmr = setTimeout(() => window.LogoPlay($("#b-preview"), JSON.parse(JSON.stringify(G)), ROOT), 250); }

  $("#b-title").oninput = e => { G.title = e.target.value; };
  $("#b-tpl").onchange = e => { G.template = e.target.value; drawForm(); };
  $("#b-groups").oninput = e => { G.groups = e.target.value; preview(); };
  $("#b-cards").addEventListener("input", e => { const f = e.target.dataset.f; if (!f) return; G.cards[+e.target.closest(".bcard").dataset.i][f] = e.target.value; preview(); });
  $("#b-cards").addEventListener("click", e => {
    const t = e.target.closest("button"); if (!t) return;
    if (t.dataset.del !== undefined) { G.cards.splice(+t.dataset.del, 1); drawForm(); }
    else if (t.dataset.up !== undefined) { const i = +t.dataset.up; if (i > 0) { [G.cards[i - 1], G.cards[i]] = [G.cards[i], G.cards[i - 1]]; drawForm(); } }
    else if (t.dataset.pick !== undefined) { pickFor = +t.dataset.pick; openPicker(); }
    else if (t.dataset.noaud !== undefined) { G.cards[+t.dataset.noaud].audio = ""; drawForm(); }
  });
  $("#b-cards").addEventListener("change", e => {
    const i = e.target.dataset.aud; if (i === undefined) return; const f = e.target.files[0]; if (!f) return;
    if (f.size > 1.5e6) { msg("Аудио больше 1,5 МБ: укоротите запись (5–10 секунд достаточно) или добавьте её через панель управления."); return; }
    const r = new FileReader(); r.onload = () => { G.cards[+i].audio = r.result; drawForm(); msg("Аудио добавлено к карточке " + (+i + 1)); }; r.readAsDataURL(f);
  });
  $("#b-add").onclick = () => { G.cards.push(card()); drawForm(); };
  $("#b-new").onclick = () => { if (confirmLike()) { G = blank(); editing = null; drawForm(); msg(""); } };
  function confirmLike() { return true; }

  /* выбор картинки */
  function openPicker() { $("#pk-q").value = ""; listPics(""); $("#b-picker").showModal(); $("#pk-q").focus(); }
  function listPics(q) {
    q = q.trim().toLowerCase();
    const items = PICS.filter(p => !q || p.w.includes(q)).slice(0, 120);
    $("#pk-list").innerHTML = (G.cards[pickFor] && G.cards[pickFor].pic ? `<div class="pic" data-p=""><div style="font-size:40px">🚫</div><b>без картинки</b></div>` : "") +
      items.map(p => `<div class="pic" data-p="${esc(p.p)}" data-w="${esc(p.w)}"><img src="${esc(src(p.p))}" alt=""><b>${esc(p.w)}</b></div>`).join("");
  }
  $("#pk-q").oninput = e => listPics(e.target.value);
  $("#pk-close").onclick = () => $("#b-picker").close();
  $("#pk-list").onclick = e => { const el = e.target.closest("[data-p]"); if (!el) return; const c = G.cards[pickFor]; c.pic = el.dataset.p; if (el.dataset.w && !c.text) c.text = el.dataset.w; $("#b-picker").close(); drawForm(); };
  $("#pk-file").onchange = e => {
    const f = e.target.files[0]; if (!f) return; const r = new FileReader();
    r.onload = () => { const img = new Image(); img.onload = () => { const s = Math.min(1, 360 / Math.max(img.width, img.height)); const cv = document.createElement("canvas"); cv.width = img.width * s; cv.height = img.height * s; cv.getContext("2d").drawImage(img, 0, 0, cv.width, cv.height); G.cards[pickFor].pic = cv.toDataURL("image/jpeg", .82); $("#b-picker").close(); drawForm(); }; img.src = r.result; };
    r.readAsDataURL(f); e.target.value = "";
  };

  /* сохранение, ссылка, файл */
  const clean = () => ({ ...G, cards: G.cards.filter(c => c.text || c.pic) });
  $("#b-save").onclick = () => {
    if (!G.title.trim()) { msg("Впишите название игры."); return; }
    const a = mine(), g = { ...clean(), id: editing || Date.now() }; const i = a.findIndex(x => x.id === g.id);
    if (i >= 0) a[i] = g; else a.unshift(g);
    if (setMine(a)) { editing = g.id; msg("Сохранено в «Мои игры» ✔"); drawMine(); }
  };
  $("#b-link").onclick = async () => {
    const g = clean(); const own = g.cards.some(c => /^data:/.test(c.pic) || /^data:/.test(c.audio || ""));
    g.cards = g.cards.map(c => ({ ...c, pic: /^data:/.test(c.pic) ? "" : c.pic, audio: /^data:/.test(c.audio || "") ? "" : c.audio }));
    const code = btoa(unescape(encodeURIComponent(JSON.stringify(g))));
    const link = new URL(ROOT + "igry/igra/index.html", location.href).href + "#g=" + code;
    try { await navigator.clipboard.writeText(link); msg("Ссылка скопирована — отправьте её родителям." + (own ? " Свои фото и аудио в ссылку не попадают — их можно добавить через панель управления." : "")); }
    catch (e) { prompt("Скопируйте ссылку:", link); }
  };
  $("#b-down").onclick = () => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(clean(), null, 1)], { type: "application/json" })); a.download = (G.title || "igra") + ".json"; a.click(); };
  $("#b-up").onchange = e => { const f = e.target.files[0]; if (!f) return; f.text().then(t => { try { G = Object.assign(blank(), JSON.parse(t)); editing = null; drawForm(); msg("Файл открыт."); } catch (er) { msg("Это не файл игры."); } }); e.target.value = ""; };

  function drawMine() {
    const a = mine();
    $("#b-mine").innerHTML = a.length ? a.map(g => `<div class="card"><h3>${esc(g.title)}</h3><p class="muted">${esc($("#b-tpl").querySelector(`[value="${g.template}"]`).textContent)} · карточек: ${g.cards.length}</p>
      <div class="btns"><button class="btn main" data-open="${g.id}">Играть</button><button class="btn soft" data-edit="${g.id}">Изменить</button><button class="btn soft" data-rm="${g.id}">Удалить</button></div></div>`).join("")
      : `<p class="muted">Пока пусто. Соберите первую игру выше.</p>`;
  }
  $("#b-mine").onclick = e => {
    const t = e.target.closest("button"); if (!t) return; const a = mine();
    if (t.dataset.edit) { G = JSON.parse(JSON.stringify(a.find(x => x.id == t.dataset.edit))); editing = G.id; drawForm(); scrollTo({ top: 0, behavior: "smooth" }); }
    if (t.dataset.rm) { setMine(a.filter(x => x.id != t.dataset.rm)); drawMine(); }
    if (t.dataset.open) { G = JSON.parse(JSON.stringify(a.find(x => x.id == t.dataset.open))); editing = G.id; drawForm(); $("#b-preview").scrollIntoView({ behavior: "smooth" }); }
  };
  drawForm(); drawMine();
})();
