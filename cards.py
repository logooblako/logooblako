# -*- coding: utf-8 -*-
"""Карточки для автоматизации звука (A4, в стиле сайта «Логооблако»).
Карточки: 1 слоги, 2 слова, 3 фраза, 4 чистоговорки, 5 пересказ, 6 скороговорки, 7 задания."""
import os, re, fitz

W, H = fitz.paper_size("a4")
M = 36
INK = (0.17, 0.16, 0.30); MUTED = (0.40, 0.40, 0.54); BG = (1, 0.976, 0.94); WHITE = (1, 1, 1)
LINE = (0.94, 0.89, 0.83)
CORAL = (1, 0.48, 0.35); MINT = (0.13, 0.72, 0.60); SKY = (0.24, 0.58, 0.95); SUN = (1, 0.75, 0.18); LAV = (0.56, 0.49, 1); PINK = (1, 0.56, 0.69)
GROUP = {"Свистящие": MINT, "Шипящие": CORAL, "Сонорные": SKY, "Заднеязычные": (0.94, 0.64, 0)}
TINT = lambda c, k=0.85: tuple(1 - (1 - x) * (1 - k) for x in c)
AREA = {"Грамматика": SKY, "Лексика": MINT, "Связная речь": LAV}
SITE = "logooblako.github.io/logooblako"


class Cards:
    def __init__(self, root, out, pics):
        self.root, self.out, self.pics = root, out, pics
        self.fr = os.path.join(root, "assets", "fonts", "Nunito-Regular.ttf")
        self.fb = os.path.join(root, "assets", "fonts", "Nunito-ExtraBold.ttf")
        self.font = {"nr": fitz.Font(fontfile=self.fr), "nb": fitz.Font(fontfile=self.fb)}
        self.cache = {}

    # ---------- базовое
    def tl(self, s, size, bold=False):
        return self.font["nb" if bold else "nr"].text_length(s, fontsize=size)

    def wrap(self, s, size, width, bold=False):
        lines, cur = [], ""
        for w in s.split():
            t = (cur + " " + w).strip()
            if self.tl(t, size, bold) <= width or not cur: cur = t
            else: lines.append(cur); cur = w
        if cur: lines.append(cur)
        return lines

    def put(self, p, x, y, s, size, bold=False, color=INK):
        p.insert_text(fitz.Point(x, y + size * 0.8), s, fontname="nb" if bold else "nr", fontsize=size, color=color)

    def para(self, p, x, y, s, size, width, bold=False, color=INK, lh=1.35):
        for ln in self.wrap(s, size, width, bold):
            self.put(p, x, y, ln, size, bold, color); y += size * lh
        return y

    def center(self, p, rect, s, size, bold=True, color=INK):
        tw = self.tl(s, size, bold)
        while tw > rect.width - 4 and size > 7: size -= 0.5; tw = self.tl(s, size, bold)
        self.put(p, rect.x0 + (rect.width - tw) / 2, rect.y0 + (rect.height - size) / 2 - 1, s, size, bold, color)

    def box(self, p, r, fill=WHITE, stroke=LINE, radius=14, width=1.2):
        rr = min(radius / max(min(r.width, r.height), 1), 0.5)
        p.draw_rect(r, color=stroke, fill=fill, width=width, radius=rr)

    def pic(self, p, word_or_path, rect):
        path = word_or_path if word_or_path.startswith("/") else self.pics.get(word_or_path.lower().strip(), "")
        full = os.path.join(self.root, path.lstrip("/")) if path else ""
        if not full or not os.path.exists(full): return False
        if full not in self.cache:
            self.cache[full] = fitz.open("pdf", fitz.open(full).convert_to_pdf())
        p.show_pdf_page(rect, self.cache[full], 0)
        return True

    def has_pic(self, w): return bool(self.pics.get(w.lower().strip()))

    def find_pic_word(self, text):
        for w in re.findall(r"[а-яёА-ЯЁ-]+", text):
            if self.has_pic(w): return w
        return None

    # ---------- страница
    def page(self, doc, s, num, title, hint):
        p = doc.new_page(width=W, height=H)
        for n, f in (("nr", self.fr), ("nb", self.fb)): p.insert_font(fontname=n, fontfile=f)
        col = GROUP.get(s.get("group"), CORAL)
        hl = self.wrap(hint, 10, W - 2 * M - 190)
        hh = max(104, 76 + 13 * len(hl) + 12)
        p.draw_rect(fitz.Rect(0, 0, W, H), color=None, fill=BG)
        p.draw_rect(fitz.Rect(0, 0, W, hh), color=None, fill=col)
        p.draw_circle(fitz.Point(W - 30, 10), 52, color=None, fill=TINT(col, 0.25))
        p.draw_circle(fitz.Point(W - 92, hh), 22, color=None, fill=TINT(col, 0.25))
        p.draw_circle(fitz.Point(M + 34, 52), 32, color=None, fill=WHITE)
        self.center(p, fitz.Rect(M + 2, 20, M + 66, 84), s["letter"], 30, True, col)
        tag = f"Карточка {num}" if num else "Задания"
        self.box(p, fitz.Rect(M + 82, 18, M + 82 + self.tl(tag, 10, True) + 20, 36), fill=TINT(col, 0.3), stroke=None, radius=9)
        self.put(p, M + 92, 21.5, tag, 10, True, WHITE)
        self.put(p, M + 82, 42, title, 20, True, WHITE)
        yy = 72
        for ln in hl: self.put(p, M + 82, yy, ln, 10, False, WHITE); yy += 13
        # подвал
        self.pic(p, "/assets/img/cloud.svg", fitz.Rect(M, H - 34, M + 24, H - 14))
        self.put(p, M + 30, H - 30, f"Логооблако · {SITE}", 8.5, True, MUTED)
        self.put(p, M + 30, H - 20, "По методическим рекомендациям Н. В. Нищевой, Ю. Б. Жихаревой-Норкиной. Картинки: Twemoji (CC-BY 4.0).", 7, False, MUTED)
        return p, hh + 18

    def heading(self, p, y, text, color):
        p.draw_circle(fitz.Point(M + 7, y + 8), 6, color=None, fill=color)
        self.put(p, M + 20, y, text, 14, True, INK)
        return y + 24

    def tracker(self, p, y, label="Отметь каждый день занятий:", n=7, color=SUN):
        self.put(p, M, y, label, 10, True, MUTED)
        x = M + self.tl(label, 10, True) + 10
        for i in range(n):
            p.draw_circle(fitz.Point(x + 9 + i * 24, y + 6), 8, color=color, width=1.6, fill=WHITE)
        return y + 22

    class Flow:
        """Простая вёрстка с переносом на новую страницу."""
        def __init__(self, c, doc, s, num, title, hint):
            self.c, self.doc, self.s, self.num, self.title, self.hint = c, doc, s, num, title, hint
            self.p, self.y = c.page(doc, s, num, title, hint)
        def need(self, h):
            if self.y + h > H - 48:
                self.p, self.y = self.c.page(self.doc, self.s, self.num, self.title + " (продолжение)", self.hint)

    # ---------- карточка 1: слоги
    def syllables(self, doc, s, col):
        f = self.Flow(self, doc, s, 1, "Автоматизация в слогах", "Взрослый читает слог, ребёнок повторяет. Каждую дорожку — 2–3 раза. Можно шагать пальчиками по слогам или нанизывать бусину на каждый слог.")
        groups = [("Открытые слоги", s.get("syl_open"), MINT), ("Закрытые слоги", s.get("syl_closed"), SKY), ("Слоги со стечением согласных", s.get("syl_cluster"), LAV)]
        for title, txt, c in groups:
            rows = [r for r in (txt or "").split("\n") if r.strip()]
            note = s.get("syl_closed_note") if title.startswith("Закрытые") else ""
            if not rows and not note: continue
            f.need(60); f.y = self.heading(f.p, f.y, title, c)
            if note:
                f.y = self.para(f.p, M + 20, f.y, note, 9.5, W - 2 * M - 20, color=MUTED) + 4
            for r in rows:
                parts = []
                for gi, g in enumerate(r.split(",")):
                    if gi: parts.append(None)
                    parts += [x.strip() for x in g.split("-") if x.strip()]
                x = M + 20; f.need(34)
                for part in parts:
                    if part is None: x += 14; continue
                    w = max(self.tl(part, 14, True) + 22, 46)
                    if x + w > W - M: x = M + 20; f.y += 34; f.need(34)
                    self.box(f.p, fitz.Rect(x, f.y, x + w, f.y + 26), fill=WHITE, stroke=c, radius=13, width=1.5)
                    self.center(f.p, fitz.Rect(x, f.y, x + w, f.y + 26), part, 14, True, INK)
                    x += w + 8
                f.y += 34
            f.y += 6
        f.need(70)
        self.box(f.p, fitz.Rect(M, f.y, W - M, f.y + 50), fill=TINT(SUN, 0.8), stroke=None)
        self.para(f.p, M + 14, f.y + 9, "Игра «Эхо»: взрослый говорит слог громко — ребёнок повторяет тихо, и наоборот. Игра «Пианино»: каждый слог — нажатие пальчиком на «клавишу» по столу.", 10, W - 2 * M - 28)
        f.y += 62; self.tracker(f.p, f.y)

    # ---------- карточка 2: слова
    def words(self, doc, s, col):
        f = self.Flow(self, doc, s, 2, "Автоматизация в словах", "Слова идут от простых к сложным. Ребёнок называет картинку, чётко произнося звук. Удалось — раскрась кружок. Переходите к следующему шагу, когда предыдущий получается легко.")
        palette = [MINT, SKY, CORAL, LAV, SUN, PINK]
        for i, st in enumerate(s.get("word_steps") or []):
            c = palette[i % len(palette)]
            words = [w.strip() for w in st["words"].split(",") if w.strip()]
            with_pic = [w for w in words if self.has_pic(w)][:6]
            rest = [w for w in words if w not in with_pic]
            h = 24 + (96 if with_pic else 0) + 22 * (1 + len(rest) // 6)
            f.need(min(h, 200)); f.y = self.heading(f.p, f.y, f"Шаг {i + 1}. {st['title']}", c)
            if with_pic:
                tw = (W - 2 * M - 20) / 6
                for k, w in enumerate(with_pic):
                    x = M + 20 + k * tw
                    r = fitz.Rect(x + 3, f.y, x + tw - 3, f.y + 88)
                    self.box(f.p, r, fill=WHITE, stroke=TINT(c, 0.4), radius=12)
                    self.pic(f.p, w, fitz.Rect(r.x0 + (r.width - 46) / 2, r.y0 + 8, r.x0 + (r.width + 46) / 2, r.y0 + 54))
                    self.center(f.p, fitz.Rect(r.x0, r.y0 + 58, r.x1, r.y0 + 76), w, 11, True)
                    f.p.draw_circle(fitz.Point(r.x1 - 10, r.y0 + 10), 5, color=c, width=1.2, fill=WHITE)
                f.y += 96
            if rest:
                x = M + 20
                for w in rest:
                    ww = self.tl(w, 11.5, True) + 30
                    if x + ww > W - M: x = M + 20; f.y += 26; f.need(26)
                    f.p.draw_circle(fitz.Point(x + 7, f.y + 9), 5, color=c, width=1.2, fill=WHITE)
                    self.put(f.p, x + 16, f.y + 2, w, 11.5, True)
                    x += ww
                f.y += 28
            f.y += 4
        f.need(60)
        self.box(f.p, fitz.Rect(M, f.y, W - M, f.y + 50), fill=TINT(SUN, 0.8), stroke=None)
        self.para(f.p, M + 14, f.y + 9, "Игры: «Назови и хлопни» — хлопок на каждый слог слова; «Где спрятался звук?» — в начале, в середине или в конце; «Подарки» — дари игрушке только слова со звуком.", 10, W - 2 * M - 28)

    # ---------- карточка 3: фраза
    def phrase(self, doc, s, col):
        f = self.Flow(self, doc, s, 3, "Автоматизация во фразе", "Сначала словосочетания, потом предложения. Ребёнок повторяет за взрослым, затем сам составляет предложение по картинке.")
        f.y = self.heading(f.p, f.y, "Словосочетания", MINT)
        items = s.get("phrases") or []
        cw = (W - 2 * M - 20) / 2
        for i, ph in enumerate(items):
            if i % 2 == 0: f.need(40)
            x = M + 20 + (i % 2) * cw
            r = fitz.Rect(x, f.y, x + cw - 8, f.y + 34)
            self.box(f.p, r, fill=WHITE, stroke=LINE, radius=12)
            w = self.find_pic_word(ph)
            tx = r.x0 + 12
            if w and self.pic(f.p, w, fitz.Rect(r.x0 + 6, r.y0 + 4, r.x0 + 32, r.y0 + 30)): tx = r.x0 + 40
            self.put(f.p, tx, r.y0 + 10, ph, 12, True)
            if i % 2 == 1 or i == len(items) - 1: f.y += 40
        f.y += 6
        f.need(60); f.y = self.heading(f.p, f.y, "Предложения", SKY)
        for i, sn in enumerate(s.get("sentences") or []):
            lines = self.wrap(sn, 12, W - 2 * M - 70)
            hh = 12 + 16 * len(lines)
            f.need(hh + 6)
            r = fitz.Rect(M + 20, f.y, W - M, f.y + hh)
            self.box(f.p, r, fill=WHITE, stroke=LINE, radius=10)
            self.center(f.p, fitz.Rect(r.x0 + 4, r.y0, r.x0 + 26, r.y1), str(i + 1), 11, True, SKY)
            yy = r.y0 + 6
            for ln in lines: self.put(f.p, r.x0 + 30, yy, ln, 12); yy += 16
            f.y += hh + 6
        f.y += 4
        pics = [w for st in s.get("word_steps") or [] for w in [x.strip() for x in st["words"].split(",")] if self.has_pic(w)]
        if pics:
            f.need(130); f.y = self.heading(f.p, f.y, "Составь предложение по картинке", LAV)
            self.put(f.p, M + 20, f.y, "Назови картинку и придумай про неё предложение: «Кто? Что делает? Где?»", 10, False, MUTED); f.y += 18
            tw = (W - 2 * M - 20) / 5
            for k, w in enumerate(pics[:5]):
                x = M + 20 + k * tw
                r = fitz.Rect(x + 3, f.y, x + tw - 3, f.y + 76)
                self.box(f.p, r, fill=WHITE, stroke=TINT(LAV, 0.4), radius=12)
                self.pic(f.p, w, fitz.Rect(r.x0 + (r.width - 50) / 2, r.y0 + 8, r.x0 + (r.width + 50) / 2, r.y0 + 58))
            f.y += 86

    # ---------- карточка 4: чистоговорки
    def chist(self, doc, s, col):
        f = self.Flow(self, doc, s, 4, "Чистоговорки", "Взрослый произносит первую часть, ребёнок повторяет всю чистоговорку. Можно отстукивать ритм ладошками или маршировать.")
        items = s.get("chistogovorki") or []
        palette = [MINT, SKY, CORAL, LAV, SUN, PINK]
        cw = (W - 2 * M) / 2
        for i, t in enumerate(items):
            parts = t.split("—", 1)
            lines = self.wrap(t, 12.5, cw - 50, True)
            hh = 18 + 17 * len(lines)
            if i % 2 == 0: f.need(hh + 10); rowh = hh
            x = M + (i % 2) * cw
            c = palette[i % len(palette)]
            r = fitz.Rect(x + 4, f.y, x + cw - 4, f.y + max(hh, 52))
            self.box(f.p, r, fill=WHITE, stroke=TINT(c, 0.4), radius=14, width=1.5)
            f.p.draw_circle(fitz.Point(r.x0 + 18, r.y0 + 18), 10, color=None, fill=TINT(c, 0.7))
            self.center(f.p, fitz.Rect(r.x0 + 8, r.y0 + 8, r.x0 + 28, r.y0 + 28), str(i + 1), 9, True, INK)
            yy = r.y0 + 10
            for ln in lines: self.put(f.p, r.x0 + 36, yy, ln, 12.5, True); yy += 17
            if i % 2 == 1 or i == len(items) - 1: f.y += max(hh, 52) + 10
        f.y += 6; f.need(80)
        self.box(f.p, fitz.Rect(M, f.y, W - M, f.y + 60), fill=TINT(SUN, 0.8), stroke=None)
        self.para(f.p, M + 14, f.y + 9, "Придумайте свою чистоговорку! Возьмите слог со звуком и подберите слово в рифму: «Ла-ла-ла — …», «Ра-ра-ра — …». Запишите её сюда:", 10, W - 2 * M - 28)
        f.p.draw_line(fitz.Point(M + 14, f.y + 50), fitz.Point(W - M - 14, f.y + 50), color=MUTED, width=0.6, dashes="[3 3] 0")
        f.y += 72; self.tracker(f.p, f.y)

    # ---------- карточка 5: пересказ
    def retell(self, doc, s, col):
        f = self.Flow(self, doc, s, 5, "Пересказ", "Прочитайте рассказ два раза. Задайте вопросы — ребёнок отвечает полным предложением. Потом ребёнок пересказывает сам, следя за звуком. Нарисуйте картинку-подсказку.")
        for i, st in enumerate(s.get("retell") or []):
            lines = self.wrap(st["text"], 12, W - 2 * M - 30)
            hh = 40 + 17 * len(lines)
            f.need(hh + 120)
            r = fitz.Rect(M, f.y, W - M, f.y + hh)
            self.box(f.p, r, fill=WHITE, stroke=TINT(col, 0.4), radius=16, width=1.5)
            self.put(f.p, r.x0 + 15, r.y0 + 12, f"{i + 1}. {st['title']}", 14, True, col)
            yy = r.y0 + 36
            for ln in lines: self.put(f.p, r.x0 + 15, yy, ln, 12); yy += 17
            f.y += hh + 10
            qx, qw = M, (W - 2 * M) * 0.58
            y0 = f.y
            self.put(f.p, qx + 4, f.y, "Вопросы:", 11, True, MUTED); f.y += 17
            for q in st.get("questions") or []:
                for ln in self.wrap("• " + q, 11, qw - 10): self.put(f.p, qx + 8, f.y, ln, 11); f.y += 15
            dr = fitz.Rect(M + qw + 10, y0, W - M, max(f.y, y0 + 90))
            self.box(f.p, dr, fill=WHITE, stroke=MUTED, radius=12, width=0.8)
            self.center(f.p, fitz.Rect(dr.x0, dr.y1 - 20, dr.x1, dr.y1 - 4), "Нарисуй картинку к рассказу", 8.5, False, MUTED)
            f.y = max(f.y, dr.y1) + 18

    # ---------- карточка 6: скороговорки
    def skor(self, doc, s, col):
        f = self.Flow(self, doc, s, 6, "Скороговорки", "Сначала медленно и чётко, потом чуть быстрее. Скороговорку можно говорить шёпотом, громко, с мячом (бросок на каждое слово) или с хлопками.")
        for i, t in enumerate(s.get("skorogovorki") or []):
            lines = self.wrap(t, 13, W - 2 * M - 130, True)
            hh = 22 + 18 * len(lines)
            f.need(hh + 10)
            r = fitz.Rect(M, f.y, W - M, f.y + hh)
            self.box(f.p, r, fill=WHITE, stroke=TINT(LAV, 0.4), radius=14, width=1.5)
            yy = r.y0 + 11
            for ln in lines: self.put(f.p, r.x0 + 16, yy, ln, 13, True); yy += 18
            for k, lab in enumerate(("медленно", "быстрее", "быстро")):
                cx = r.x1 - 98 + k * 34
                f.p.draw_circle(fitz.Point(cx, r.y0 + hh / 2 - 4), 9, color=LAV, width=1.4, fill=WHITE)
                self.center(f.p, fitz.Rect(cx - 17, r.y0 + hh / 2 + 6, cx + 17, r.y0 + hh / 2 + 16), lab, 6.5, False, MUTED)
            f.y += hh + 10
        f.y += 6; f.need(60)
        self.box(f.p, fitz.Rect(M, f.y, W - M, f.y + 52), fill=TINT(SUN, 0.8), stroke=None)
        self.para(f.p, M + 14, f.y + 9, "Скороговорки — народные, подобраны от коротких к длинным по принципу сборников Т. А. Куликовской. Давайте их, только когда звук уже уверенно звучит во фразе.", 10, W - 2 * M - 28)
        f.y += 66
        if H - 60 - f.y > 140:
            r = fitz.Rect(M, f.y, W - M, H - 60)
            self.box(f.p, r, fill=WHITE, stroke=MUTED, radius=16, width=0.8)
            self.center(f.p, fitz.Rect(r.x0, r.y0 + 10, r.x1, r.y0 + 28), "Нарисуй картинку к любимой скороговорке", 12, True, MUTED)

    # ---------- карточка 7: задания
    def tasks(self, doc, s, col):
        f = self.Flow(self, doc, s, 7, "Задания для развития речи", "Грамматика, словарь и связная речь. Задания в стиле домашних тетрадей Ю. Б. Жихаревой-Норкиной: ребёнок отвечает полным ответом и следит за звуком.")
        for t in s.get("tasks") or []:
            c = AREA.get(t["area"], CORAL)
            items = t.get("items") or []
            cols = 2 if all(len(x) < 40 for x in items) else 1
            cw = (W - 2 * M - 28) / cols
            per = (len(items) + cols - 1) // cols
            colines = [sum(len(self.wrap(x, 11, cw - 40)) for x in items[ci * per:(ci + 1) * per]) for ci in range(cols)]
            hh = 56 + max(colines) * 17
            f.need(hh + 10)
            r = fitz.Rect(M, f.y, W - M, f.y + hh)
            self.box(f.p, r, fill=WHITE, stroke=TINT(c, 0.4), radius=14, width=1.5)
            lab = t["area"]
            self.box(f.p, fitz.Rect(r.x0 + 12, r.y0 + 10, r.x0 + 24 + self.tl(lab, 8.5, True), r.y0 + 24), fill=TINT(c, 0.75), stroke=None, radius=7)
            self.put(f.p, r.x0 + 18, r.y0 + 12.5, lab, 8.5, True, INK)
            self.put(f.p, r.x0 + 32 + self.tl(lab, 8.5, True), r.y0 + 9, t["title"], 13, True)
            self.put(f.p, r.x0 + 14, r.y0 + 30, t["instruction"], 10, False, MUTED)
            yy0 = r.y0 + 48
            per = (len(items) + cols - 1) // cols
            for ci in range(cols):
                yy = yy0
                for x in items[ci * per:(ci + 1) * per]:
                    xx = r.x0 + 14 + ci * cw
                    w = self.find_pic_word(x)
                    if w and self.pic(f.p, w, fitz.Rect(xx, yy - 2, xx + 18, yy + 16)): xx += 24
                    else:
                        f.p.draw_circle(fitz.Point(xx + 5, yy + 7), 3, color=None, fill=c); xx += 14
                    for ln in self.wrap(x, 11, cw - 40): self.put(f.p, xx, yy, ln, 11); yy += 17
            f.y += hh + 10

    # ---------- всё вместе
    def sound(self, s, base):
        col = GROUP.get(s.get("group"), CORAL)
        steps = [("syllables", "1. Автоматизация в слогах", "slogi"), ("words", "2. Автоматизация в словах", "slova"),
                 ("phrase", "3. Автоматизация во фразе", "fraza"), ("chist", "4. Чистоговорки", "chistogovorki"),
                 ("retell", "5. Пересказы", "pereskaz"), ("skor", "6. Скороговорки", "skorogovorki"),
                 ("tasks", "7. Задания: грамматика, словарь, связная речь", "zadaniya")]
        files, alldoc = [], fitz.open()
        for meth, title, suffix in steps:
            doc = fitz.open(); getattr(self, meth)(doc, s, col)
            if not len(doc): continue
            alldoc.insert_pdf(doc)
            rel = f"{base}-{suffix}.pdf"; self.save(doc, rel)
            files.append({"title": title, "file": "/" + rel, "key": meth})
        rel = f"{base}-vse-kartochki.pdf"; self.save(alldoc, rel)
        return files, {"title": "Все карточки одним файлом", "file": "/" + rel}

    def save(self, doc, rel):
        dst = os.path.join(self.out, rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
        doc.save(dst, garbage=3, deflate=True); doc.close()


    # ---------- фонематический слух
    def fonematika(self, f, base):
        s = {"letter": "Ф", "group": "Сонорные"}
        files = []
        doc = fitz.open()
        fl = self.Flow(self, doc, s, None, "Игры для фонематического слуха", "Шесть этапов — от неречевых звуков к звуковому анализу слова. По программам Т. Б. Филичевой, Г. В. Чиркиной, Т. В. Тумановой.")
        palette = [MINT, SKY, CORAL, LAV, SUN, PINK]
        for i, st in enumerate(f.get("stages") or []):
            c = palette[i % 6]
            fl.need(80); fl.y = self.heading(fl.p, fl.y, f"Этап {i + 1}. {st['title']}", c)
            fl.y = self.para(fl.p, M + 20, fl.y, st["goal"], 10, W - 2 * M - 20, color=MUTED) + 4
            for g in st.get("games") or []:
                lines = self.wrap(g["how"], 10.5, W - 2 * M - 40)
                hh = 26 + 14 * len(lines)
                fl.need(hh + 6)
                r = fitz.Rect(M + 20, fl.y, W - M, fl.y + hh)
                self.box(fl.p, r, fill=WHITE, stroke=TINT(c, 0.4), radius=12)
                self.put(fl.p, r.x0 + 12, r.y0 + 7, g["title"], 11.5, True)
                yy = r.y0 + 23
                for ln in lines: self.put(fl.p, r.x0 + 12, yy, ln, 10.5); yy += 14
                fl.y += hh + 6
            fl.y += 6
        self.save(doc, base + "-igry.pdf"); files.append({"title": "Игры по этапам (памятка)", "file": "/" + base + "-igry.pdf"})

        def picgrid(title, hint, words, draw_under, fname, label):
            doc = fitz.open(); p, y = self.page(doc, s, None, title, hint)
            cols, cw = 3, (W - 2 * M) / 3
            ch = (H - y - 60) / 4
            for k, w in enumerate(words[:12]):
                x0 = M + (k % cols) * cw; y0 = y + (k // cols) * ch
                r = fitz.Rect(x0 + 5, y0 + 5, x0 + cw - 5, y0 + ch - 5)
                self.box(p, r, fill=WHITE, stroke=LINE, radius=14)
                sz = min(r.width, r.height) * 0.48
                self.pic(p, w, fitz.Rect(r.x0 + (r.width - sz) / 2, r.y0 + 10, r.x0 + (r.width + sz) / 2, r.y0 + 10 + sz))
                self.center(p, fitz.Rect(r.x0, r.y0 + 14 + sz, r.x1, r.y0 + 32 + sz), w, 12, True)
                draw_under(p, r, w)
            self.save(doc, fname); files.append({"title": label, "file": "/" + fname})

        def cells(n, color):
            def d(p, r, w):
                cw = 26; x = r.x0 + (r.width - n * cw) / 2; y = r.y1 - 36
                for i in range(n): self.box(p, fitz.Rect(x + i * cw, y, x + i * cw + cw - 2, y + 24), fill=WHITE, stroke=color, radius=5, width=1.4)
            return d
        def circles(n, color):
            def d(p, r, w):
                x = r.x0 + (r.width - n * 26) / 2; y = r.y1 - 22
                for i in range(n): p.draw_circle(fitz.Point(x + 13 + i * 26, y), 9, color=color, width=1.4, fill=WHITE)
            return d
        sw = [w for w in ["сок", "сова", "лиса", "весы", "нос", "ананас", "автобус", "маска", "сумка", "кокос", "бусы", "сыр"] if self.has_pic(w)]
        picgrid("Где спрятался звук [С]?", "Назови картинку. Где ты слышишь звук [С] — в начале, в середине или в конце слова? Поставь фишку или крестик в нужную клеточку.", sw, cells(3, MINT), base + "-gde-zvuk.pdf", "Где спрятался звук? (картинки)")
        mix = [w for w in ["кот", "сыр", "сок", "рак", "кит", "рыба", "роза", "сова", "лиса", "машина", "ракета", "собака", "черепаха", "кукуруза", "помидор"] if self.has_pic(w)]
        picgrid("Сколько слогов?", "Назови картинку и прохлопай слово. Сколько хлопков — столько кружков раскрась.", mix, circles(4, SKY), base + "-slogi.pdf", "Сколько слогов? (картинки)")
        three = [w for w in ["кот", "сок", "сыр", "рак", "кит", "мак", "лук", "жук", "суп", "нос", "дом", "сом"] if self.has_pic(w)]
        picgrid("Звуковой анализ: живые звуки", "Назови звуки по порядку и выложи под картинкой фишки: красная — гласный, синяя — твёрдый согласный, зелёная — мягкий.", three, cells(3, CORAL), base + "-analiz.pdf", "Звуковой анализ слов из трёх звуков")
        first = [w for w in ["аист", "утка", "ослик", "иглы", "арбуз", "облако", "улитка", "ананас", "апельсин", "окно", "уши", "автобус"] if self.has_pic(w)]
        if len(first) >= 6:
            picgrid("Первый звук", "Назови картинку. Какой звук ты слышишь первым? Нарисуй в клеточке кружок того цвета, который вы выбрали для этого звука.", first, cells(1, LAV), base + "-pervyy-zvuk.pdf", "Первый звук в слове")
        return files
