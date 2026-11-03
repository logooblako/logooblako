# -*- coding: utf-8 -*-
"""Сборка сайта «Логооблако»: content/*.md -> _site/*.html + PDF-листы.
Запуск: python build.py   (нужны pyyaml, markdown, jinja2, pymupdf)"""
import os, re, glob, json, shutil, yaml, markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
import worksheets, cards

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_site")

def load(path):
    t = open(path, encoding="utf8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", t, re.S)
    fm, body = (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, t)
    fm["slug"] = os.path.splitext(os.path.basename(path))[0]
    body = body.strip()
    fm["body_html"] = body if body.startswith("<") else markdown.markdown(body, extensions=["extra"])
    return fm

def coll(name):
    items = [load(p) for p in glob.glob(os.path.join(ROOT, "content", name, "*.md"))]
    return sorted(items, key=lambda x: (x.get("order") or 999, x["slug"]))

def page(name):
    p = os.path.join(ROOT, "content", "pages", name + ".md")
    return load(p) if os.path.exists(p) else {"title": "", "body_html": ""}

site = load(os.path.join(ROOT, "data", "site.md"))
env = Environment(loader=FileSystemLoader(os.path.join(ROOT, "templates")), autoescape=select_autoescape(["html"]))

def render(tpl, rel, **ctx):
    depth = rel.count("/")
    root = "../" * depth
    def u(p):
        if not p: return ""
        if re.match(r"^(https?:|mailto:|#)", p): return p
        return root + p.lstrip("/")
    env.globals.update(u=u, root=root, site=site)
    html = env.get_template(tpl).render(**ctx)
    dst = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf8").write(html)

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    for d in ("assets", "media"):
        if os.path.exists(os.path.join(ROOT, d)):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(OUT, d), ignore=shutil.ignore_patterns("fonts"))
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    sounds, diffs, levels = coll("sounds"), coll("diffs"), coll("levels")
    motor, reading, cognition = coll("motor"), coll("reading"), coll("cognition")
    groups = []
    for s in sounds:
        if not groups or groups[-1][0] != s["group"]: groups.append((s["group"], []))
        groups[-1][1].append(s)

    pdf = worksheets.Maker(ROOT, OUT)
    pics = {os.path.splitext(f)[0]: "/assets/pics/" + f for f in os.listdir(os.path.join(ROOT, "assets", "pics"))}
    tr = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя", ["a","b","v","g","d","e","yo","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","h","c","ch","sh","sch","","y","","e","yu","ya"]))
    class PicMap(dict):
        def get(self, w, d=""):
            if w in self: return self[w]
            return pics.get("".join(tr.get(c, c) for c in w.lower()).replace(" ", "-"), d)
    picmap = PicMap()
    for s in sounds:
        for k in ("words_start", "words_middle", "words_end"):
            for w in s.get(k) or []:
                if w.get("pic"): picmap[w["word"].lower()] = w["pic"]
    cm = cards.Cards(ROOT, OUT, picmap)
    for s in sounds:
        s["auto_files"] = pdf.sound(s)
        s["cards"], s["cards_all"] = cm.sound(s, f"files/zvuki/{s['slug']}")
        s["card"] = {c["key"]: c for c in s["cards"]}
        s["all_words"] = [w for k in ("words_start", "words_middle", "words_end") for w in (s.get(k) or []) if w.get("pic")]
    for d in diffs: d["auto_files"] = pdf.diff(d)
    for l in levels: l["auto_files"] = pdf.level(l)
    motor_files = pdf.motor()

    render("home.html", "index.html", nav="home", sounds=sounds, diffs=diffs)
    render("sounds_index.html", "zvuki/index.html", nav="zvuki", groups=groups)
    for s in sounds:
        render("sound.html", f"zvuki/{s['slug']}/index.html", nav="zvuki", s=s, groups=groups,
               game=json.dumps([{"w": w["word"], "p": w["pic"]} for w in s["all_words"]], ensure_ascii=False))
    fon = load(os.path.join(ROOT, "content", "fonematika.md"))
    render("fonematika.html", "fonematika/index.html", nav="fonematika", f=fon, files=cm.fonematika(fon, "files/fonematika/fonematika"))
    render("diffs_index.html", "differentsiatsiya/index.html", nav="diff", diffs=diffs)
    for d in diffs:
        g = [{"w": w["word"], "p": w["pic"], "h": "a"} for w in d.get("words_a") or [] if w.get("pic")] + \
            [{"w": w["word"], "p": w["pic"], "h": "b"} for w in d.get("words_b") or [] if w.get("pic")]
        render("diff.html", f"differentsiatsiya/{d['slug']}/index.html", nav="diff", d=d, diffs=diffs, game=json.dumps(g, ensure_ascii=False))
    render("levels_index.html", "urovni/index.html", nav="urovni", levels=levels, intro=page("levels-intro"))
    for l in levels:
        render("level.html", f"urovni/{l['slug']}/index.html", nav="urovni", l=l, levels=levels)
    render("motor.html", "motorika/index.html", nav="motorika", ages=motor, intro=page("motor-intro"), files=motor_files)
    render("reading.html", "chitat/index.html", nav="chitat", ages=reading, intro=page("reading-intro"))
    render("cognition.html", "poznanie/index.html", nav="poznanie", ages=cognition, intro=page("cognition-intro"))
    render("author.html", "avtor/index.html", nav="avtor", a=load(os.path.join(ROOT, "content", "author.md")))
    games = coll("games")
    names = {"quiz": "Викторина", "pairs": "Найди пару", "sort": "Разложи по группам", "wheel": "Колесо", "flip": "Переверни карточку", "slides": "Презентация"}
    render("games_index.html", "igry/index.html", nav="igry", games=games, names=names)
    pics = {}
    for coll_items, keys in ((sounds, ("words_start", "words_middle", "words_end")), (diffs, ("words_a", "words_b"))):
        for it in coll_items:
            for k in keys:
                for w in it.get(k) or []:
                    if w.get("pic"): pics.setdefault(w["pic"], w["word"])
    for f in sorted(os.listdir(os.path.join(ROOT, "assets", "pics"))):
        pth = "/assets/pics/" + f
        if not f.startswith("m-"): pics.setdefault(pth, os.path.splitext(f)[0].replace("-", " "))
    pic_list = sorted(({"w": w, "p": p} for p, w in pics.items()), key=lambda x: x["w"])
    render("builder.html", "igry/sozdat/index.html", nav="igry", pics=json.dumps(pic_list, ensure_ascii=False))
    render("game.html", "igry/igra/index.html", nav="igry", g={"title": "Игра", "description": "", "body_html": ""}, data=json.dumps({"template": "flip", "cards": []}), shared=True)
    for g in games:
        data = {"template": g.get("template"), "groups": g.get("groups") or "", "cards": g.get("cards") or []}
        render("game.html", f"igry/{g['slug']}/index.html", nav="igry", g=g, data=json.dumps(data, ensure_ascii=False))
    tales = coll("tales")
    render("tales_index.html", "skazki/index.html", nav="skazki", tales=tales, intro=page("tales-intro"))
    for t in tales:
        render("tale.html", f"skazki/{t['slug']}/index.html", nav="skazki", t=t)
    reviews = sorted([r for r in coll("reviews") if r.get("published", True)], key=lambda r: str(r.get("date") or ""), reverse=True)
    render("feedback.html", "otzyvy/index.html", nav="otzyvy", reviews=reviews)
    ai = [x for x in coll("ai") if x.get("published", True)]
    render("ai.html", "ii/index.html", nav="ii", items=ai, intro=page("ai-intro"))
    render("404.html", "404.html", nav="")
    base = (site.get("site_url") or "").rstrip("/")
    if base:
        urls = []
        for dp, dn, fn in os.walk(OUT):
            for f in fn:
                if f == "index.html":
                    rel = os.path.relpath(os.path.join(dp, f), OUT).replace(os.sep, "/")
                    urls.append(base + "/" + rel.replace("index.html", ""))
        open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{x}</loc></url>\n" for x in sorted(urls)) + "</urlset>\n")
        open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    print("Готово:", OUT)

if __name__ == "__main__":
    main()
