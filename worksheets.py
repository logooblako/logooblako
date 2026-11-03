# -*- coding: utf-8 -*-
"""PDF-листы для печати (A4). Картинки — SVG из assets/pics, шрифт Nunito."""
import os, math, fitz

INK = (0.17, 0.16, 0.30); MUTED = (0.45, 0.45, 0.58); CORAL = (1, 0.48, 0.35); MINT = (0.13, 0.72, 0.60)
SKY = (0.24, 0.58, 0.95); SUN = (1, 0.75, 0.18); LINE = (0.88, 0.84, 0.78)
W, H = fitz.paper_size("a4")

class Maker:
    def __init__(self, root, out):
        self.root, self.out = root, out
        self.font_r = os.path.join(root, "assets", "fonts", "Nunito-Regular.ttf")
        self.font_b = os.path.join(root, "assets", "fonts", "Nunito-ExtraBold.ttf")
        self.cache = {}

    # --- базовые помощники
    def new(self):
        doc = fitz.open(); return doc
    def pg(self, doc, title, subtitle=""):
        p = doc.new_page(width=W, height=H)
        p.insert_font(fontname="nr", fontfile=self.font_r); p.insert_font(fontname="nb", fontfile=self.font_b)
        p.draw_rect(fitz.Rect(0, 0, W, 8), color=None, fill=CORAL)
        self.text(p, fitz.Rect(40, 28, W - 40, 70), title, 22, bold=True)
        if subtitle: self.text(p, fitz.Rect(40, 62, W - 40, 100), subtitle, 12, color=MUTED)
        self.text(p, fitz.Rect(40, H - 30, W - 40, H - 12), "«" + "Логооблако" + "» — материалы для занятий дома. Картинки: Twemoji (CC-BY 4.0).", 8, color=MUTED)
        return p
    def text(self, p, rect, s, size, bold=False, color=INK, align=0):
        rc = p.insert_textbox(rect, s, fontname="nb" if bold else "nr", fontsize=size, color=color, align=align)
        return rc
    def pic(self, p, rel, rect):
        path = os.path.join(self.root, rel.lstrip("/")) if rel else ""
        if not rel or not os.path.exists(path): return
        if path not in self.cache:
            src = fitz.open(path); self.cache[path] = fitz.open("pdf", src.convert_to_pdf())
        p.show_pdf_page(rect, self.cache[path], 0)
    def save(self, doc, rel):
        dst = os.path.join(self.out, rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
        doc.save(dst, garbage=3, deflate=True); doc.close(); return "/" + rel

    def grid(self, p, words, top, cols=3, rows=4, circle=True):
        cw = (W - 80) / cols; ch = (H - top - 60) / rows
        for i, w in enumerate(words[:cols * rows]):
            c, r = i % cols, i // cols
            x, y = 40 + c * cw, top + r * ch
            p.draw_rect(fitz.Rect(x + 6, y + 6, x + cw - 6, y + ch - 6), color=LINE, width=1.5, radius=0.12)
            s = min(cw, ch) * 0.52
            self.pic(p, w.get("pic"), fitz.Rect(x + (cw - s) / 2, y + 16, x + (cw + s) / 2, y + 16 + s))
            self.text(p, fitz.Rect(x + 10, y + ch - 50, x + cw - 10, y + ch - 20), w["word"], 15, bold=True, align=1)
            if circle: p.draw_circle(fitz.Point(x + cw - 24, y + 24), 9, color=MINT, width=1.5)

    # --- звуки
    def sound(self, s):
        words = [w for k in ("words_start", "words_middle", "words_end") for w in (s.get(k) or []) if w.get("pic")]
        files = []; base = f"files/zvuki/{s['slug']}"
        if words:
            doc = self.new()
            for i in range(0, len(words), 12):
                p = self.pg(doc, f"{s['title']}: назови картинки", "Назови картинку, правильно произнося звук. Если получилось — раскрась кружок.")
                self.grid(p, words[i:i + 12], 110)
            files.append({"title": "Назови картинки (карточки)", "file": self.save(doc, base + "-kartinki.pdf")})
            doc = self.new(); p = self.pg(doc, f"{s['title']}: дорожка", "Бросай кубик, шагай по кружкам и называй картинки на своём пути.")
            pts = []
            for r in range(4):
                xs = list(range(4)) if r % 2 == 0 else list(range(3, -1, -1))
                for c in xs: pts.append((80 + c * 145, 170 + r * 160))
            for a, b in zip(pts, pts[1:]): p.draw_line(fitz.Point(*a), fitz.Point(*b), color=SUN, width=14)
            for i, (x, y) in enumerate(pts):
                p.draw_circle(fitz.Point(x, y), 52, color=SUN, fill=(1, 1, 1), width=4)
                w = words[i % len(words)]; self.pic(p, w["pic"], fitz.Rect(x - 30, y - 34, x + 30, y + 26))
                self.text(p, fitz.Rect(x - 50, y + 22, x + 50, y + 44), w["word"], 10, bold=True, align=1)
            self.text(p, fitz.Rect(30, 100, 160, 130), "СТАРТ", 14, bold=True, color=CORAL)
            self.text(p, fitz.Rect(30, 712, 200, 740), "ФИНИШ", 14, bold=True, color=CORAL)
            files.append({"title": "Игра-дорожка", "file": self.save(doc, base + "-dorozhka.pdf")})
        return files

    # --- дифференциация
    def diff(self, d):
        files = []; base = f"files/diff/{d['slug']}"
        wa = [w for w in d.get("words_a") or [] if w.get("pic")]; wb = [w for w in d.get("words_b") or [] if w.get("pic")]
        if wa and wb:
            doc = self.new(); p = self.pg(doc, f"Разложи по домикам: {d['title']}", "Вырежи картинки. Назови каждую и положи в домик с нужным звуком.")
            for i, (letter, col) in enumerate(((d["sound_a"], MINT), (d["sound_b"], CORAL))):
                x = 50 + i * (W - 100) / 2; w = (W - 140) / 2
                p.draw_polyline([fitz.Point(x, 220), fitz.Point(x + w / 2, 120), fitz.Point(x + w, 220)], color=col, fill=col, closePath=True)
                p.draw_rect(fitz.Rect(x + 15, 220, x + w - 15, 330), color=col, width=4, radius=0.06)
                tw = fitz.Font(fontfile=self.font_b).text_length(letter, fontsize=56); p.insert_text(fitz.Point(x + (w - tw) / 2, 296), letter, fontname="nb", fontsize=56, color=col)
            mixed = [v for pair in zip(wa, wb) for v in pair] + wa[len(wb):] + wb[len(wa):]
            cw, ch = (W - 80) / 4, 140
            for i, w in enumerate(mixed[:12]):
                c, r = i % 4, i // 4; x, y = 40 + c * cw, 370 + r * ch
                p.draw_rect(fitz.Rect(x + 4, y + 4, x + cw - 4, y + ch - 4), color=MUTED, width=0.8, dashes="[4 4] 0")
                self.pic(p, w["pic"], fitz.Rect(x + cw / 2 - 40, y + 14, x + cw / 2 + 40, y + 94))
                self.text(p, fitz.Rect(x + 6, y + 100, x + cw - 6, y + 126), w["word"], 12, bold=True, align=1)
            files.append({"title": "Разложи по домикам (вырезать)", "file": self.save(doc, base + "-domiki.pdf")})
        doc = self.new(); p = self.pg(doc, f"Различаем звуки {d['title']}", "Сначала ребёнок слушает и показывает, потом повторяет сам.")
        y = 110
        def block(title, lines):
            nonlocal y
            if not lines: return
            self.text(p, fitz.Rect(40, y, W - 40, y + 22), title, 15, bold=True, color=CORAL); y += 26
            for ln in lines: self.text(p, fitz.Rect(56, y, W - 40, y + 24), "• " + ln, 14); y += 23
            y += 8
        block("Слоговые ряды", d.get("syllable_pairs") or [])
        block("Слова, которые отличаются одним звуком", [f"{x['a']} — {x['b']}" for x in d.get("word_pairs") or []])
        block("Предложения", d.get("sentences") or [])
        block("Скороговорки", d.get("skorogovorki") or [])
        files.append({"title": "Слоги, пары слов, предложения", "file": self.save(doc, base + "-slova.pdf")})
        return files

    # --- уровни речи: памятка
    def level(self, l):
        doc = self.new(); p = self.pg(doc, f"Памятка для родителей: {l['title'].lower()} речевого развития", l.get("subtitle", ""))
        y = 110
        def block(title, lines):
            nonlocal y, p
            for i, ln in enumerate(lines):
                if i == 0:
                    if y > H - 120: p = self.pg(doc, "Памятка (продолжение)"); y = 110
                    self.text(p, fitz.Rect(40, y, W - 40, y + 22), title, 15, bold=True, color=CORAL); y += 26
                h = 18 * (1 + len(ln) // 85)
                if y + h > H - 50: p = self.pg(doc, "Памятка (продолжение)"); y = 110
                self.text(p, fitz.Rect(56, y, W - 40, y + h + 6), "• " + ln, 11.5); y += h + 4
            y += 8
        block("Как разговаривать с ребёнком", l.get("talk") or [])
        block("Дома", l.get("home") or [])
        block("Куда сходить", l.get("places") or [])
        block("Сказки и книги", l.get("tales") or [])
        block("Как читать сказки", l.get("tale_how") or [])
        block("Какие вопросы задавать после сказки", l.get("tale_questions") or [])
        return [{"title": "Памятка (PDF)", "file": self.save(doc, f"files/urovni/uroven-{l['slug']}.pdf")}]

    # --- мелкая моторика: дорожки и линии для вырезания
    def motor(self):
        files = []
        doc = self.new(); p = self.pg(doc, "Обведи дорожки", "Проведи пальчиком, потом карандашом от зверька к угощению, не отрывая руки.")
        rows = [("line", "1f430", "1f955"), ("wave", "1f41d", "1f33c"), ("zig", "1f42d", "1f9c0"), ("loop", "1f436", "1f9b4")]
        for i, (kind, a, b) in enumerate(rows):
            y = 170 + i * 165; x0, x1 = 120, W - 120
            pts = []
            for k in range(61):
                t = k / 60; x = x0 + (x1 - x0) * t
                if kind == "line": yy = y
                elif kind == "wave": yy = y + 30 * math.sin(t * math.pi * 4)
                elif kind == "zig": yy = y + (30 if int(t * 8) % 2 else -30) * (1 - abs((t * 8) % 1 * 2 - 1)) * 2 - 0
                else: yy = y + 30 * math.sin(t * math.pi * 6); x = x + 18 * math.cos(t * math.pi * 6)
                pts.append(fitz.Point(x, yy))
            if kind == "zig":
                pts = [fitz.Point(x0 + (x1 - x0) * k / 8, y + (-30 if k % 2 else 30)) for k in range(9)]
            p.draw_polyline(pts, color=MUTED, width=3, dashes="[6 6] 0")
            for code, xx in ((a, 40), (b, W - 110)):
                self.pic(p, f"/assets/pics/m-{code}.svg", fitz.Rect(xx, y - 35, xx + 70, y + 35))
        files.append({"title": "Обведи дорожки", "file": self.save(doc, "files/motorika/obvedi-dorozhki.pdf")})
        doc = self.new(); p = self.pg(doc, "Вырежи по линии", "Детскими ножницами разрежь полоски по линиям: прямой, волнистой, ломаной.")
        for i in range(6):
            y = 130 + i * 110; p.draw_rect(fitz.Rect(40, y, W - 40, y + 90), color=LINE, fill=[(1, .95, .9), (.92, .97, 1), (.93, 1, .96)][i % 3], width=1)
            x0, x1, yc = 60, W - 60, y + 45
            if i < 2: pts = [fitz.Point(x0, yc), fitz.Point(x1, yc)]
            elif i < 4: pts = [fitz.Point(x0 + (x1 - x0) * k / 80, yc + 18 * math.sin(k / 80 * math.pi * 6)) for k in range(81)]
            else: pts = [fitz.Point(x0 + (x1 - x0) * k / 10, yc + (-18 if k % 2 else 18)) for k in range(11)]
            p.draw_polyline(pts, color=INK, width=2.2, dashes="[8 5] 0")
            p.draw_circle(fitz.Point(52, yc), 5, color=CORAL, fill=CORAL)
        files.append({"title": "Вырежи по линии", "file": self.save(doc, "files/motorika/vyrezhi-po-linii.pdf")})
        return files
