# -*- coding: utf-8 -*-
"""Наполняет страницы звуков материалами для автоматизации из tools/auto/*.txt.
Запускается один раз: дописывает поля в content/sounds/*.md (дальше правится через панель)."""
import os, re, glob, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse(text):
    out = {}
    for block in re.split(r"^@@ ", text, flags=re.M)[1:]:
        slug, rest = block.split("\n", 1)
        d = {}
        for sec in re.split(r"^## ", rest, flags=re.M)[1:]:
            name, body = sec.split("\n", 1)
            lines = [l.strip() for l in body.strip().split("\n") if l.strip()]
            d[name.strip()] = lines
        out[slug.strip()] = d
    return out

def retell(lines):
    res, cur = [], None
    for l in lines:
        if l.startswith("# "):
            cur = {"title": l[2:].strip(), "text": "", "questions": []}; res.append(cur)
        elif l.startswith("? "): cur["questions"].append(l[2:].strip())
        else: cur["text"] = (cur["text"] + " " + l).strip()
    return res

def tasks(lines):
    res = []
    for l in lines:
        m = re.match(r"\[(.+?)\]\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+)$", l)
        area, title, instr, items = m.groups()
        res.append({"area": area, "title": title, "instruction": instr, "items": [x.strip() for x in items.split(";") if x.strip()]})
    return res

def merge(old, new):
    seen, res = set(), []
    for x in (old or []) + new:
        k = x.lower().strip(" .!")
        if k not in seen: seen.add(k); res.append(x)
    return res

data = {}
for f in sorted(glob.glob(os.path.join(ROOT, "tools", "auto", "*.txt"))):
    data.update(parse(open(f, encoding="utf8").read()))

for slug, d in data.items():
    path = os.path.join(ROOT, "content", "sounds", slug + ".md")
    t = open(path, encoding="utf8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", t, re.S)
    fm, body = yaml.safe_load(m.group(1)), m.group(2)
    fm.pop("syllables", None)
    fm["syl_open"] = "\n".join(d.get("open", []))
    fm["syl_closed"] = "\n".join(d.get("closed", []))
    fm["syl_closed_note"] = " ".join(d.get("closed_note", []))
    fm["syl_cluster"] = "\n".join(d.get("cluster", []))
    steps = []
    for l in d.get("words", []):
        title, words = l.split(":", 1)
        steps.append({"title": title.strip(), "words": words.strip()})
    fm["word_steps"] = steps
    fm["phrases"] = merge(fm.get("phrases"), d.get("phrases", []))
    fm["sentences"] = merge(fm.get("sentences"), d.get("sentences", []))
    fm["chistogovorki"] = merge(fm.get("chistogovorki"), d.get("chist", []))
    fm["skorogovorki"] = merge(fm.get("skorogovorki"), d.get("skor", []))
    fm["retell"] = retell(d.get("retell", []))
    fm["tasks"] = tasks(d.get("tasks", []))
    open(path, "w", encoding="utf8").write("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + body.lstrip("\n"))
    print("ok", slug, len(steps), len(fm["tasks"]))
