# -*- coding: utf-8 -*-
"""Докачивает картинки Twemoji для карточек автоматизации (assets/pics/<слово>.svg)."""
import os, sys, shutil, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICS = os.path.join(ROOT, "assets", "pics")

def slug(word):
    tr = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
      ["a","b","v","g","d","e","yo","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","h","c","ch","sh","sch","","y","","e","yu","ya"]))
    return "".join(tr.get(c, c) for c in word.lower()).replace(" ", "-")

NEW = {
 "пёс":"1f415","стакан":"1f95b","сосна":"1f332","глобус":"1f30d","вагон":"1f683","трактор":"1f69c","трава":"1f33f",
 "кран":"1f3d7","гроза":"26c8","гром":"26c8","ведро":"1faa3","дрова":"1fab5","корона":"1f451","паровоз":"1f682",
 "ворона":"1f426-200d-2b1b","рубашка":"1f455","рюкзак":"1f392","лошадь":"1f40e","футбол":"26bd","орёл":"1f985",
 "клоун":"1f921","яблоко":"1f34e","колокол":"1f514","клён":"1f341","блины":"1f95e","флейта":"1fa88","портфель":"1f4bc",
 "соль":"1f9c2","пальто":"1f9e5","шапка":"1f9e2","шуба":"1f9e5","чашка":"2615","школа":"1f3eb","нож":"1f52a","ножи":"1f52a",
 "жонглёр":"1f939","чай":"1f375","туча":"2601","ночь":"1f303","солнце":"2600","отец":"1f468","дворец":"1f3f0",
 "палец":"1f446","цифра":"1f522","лицо":"1f600","кофта":"1f9e5","банка":"1fad9","окно":"1fa9f","вилка":"1f374",
 "каток":"26f8","халат":"1f97c","хоккей":"1f3d2","яхта":"26f5","каска":"26d1","самосвал":"1f69a","свеча":"1f56f",
 "ваза":"1f3fa","змей":"1fa81","изба":"1f6d6","гнездо":"1fab9","бизон":"1f9ac","музей":"1f3db","змея":"1f40d",
 "бензин":"26fd","арбуз":"1f349","улитка":"1f40c","облако":"2601","ослик":"1facf","дом":"1f3e0","аист":"1fabd","барабанщик":"1f941","кружка":"2615","лампа":"1f4a1","кольцо":"1f48d","мак":"1f33a","мишка":"1f9f8",
}
ALIAS = {"гуси":"гусь","грибы":"гриб","орехи":"орех","носок":"носки","снег":"снежинка","зайка":"заяц","шар":"шарик",
         "ёж":"ёжик","ежи":"ёжик","булка":"хлеб","дочка":"девочка","лапа":"лапы","сани":"санки","петухи":"петух",
         "кошечка":"кошка","овцы":"овца","огурцы":"огурец","цветы":"цветок","звёзды":"звезда","лапы":"лапы"}

for w, code in NEW.items():
    fn = os.path.join(PICS, slug(w) + ".svg")
    if os.path.exists(fn): continue
    ok = False
    for c in (code, code + "-fe0f"):
        try:
            data = urllib.request.urlopen(f"https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/svg/{c}.svg", timeout=30).read()
            if data.lstrip().startswith(b"<svg"): open(fn, "wb").write(data); ok = True; break
        except Exception: pass
    print("ok " if ok else "НЕТ", w)
for a, w in ALIAS.items():
    src, dst = os.path.join(PICS, slug(w) + ".svg"), os.path.join(PICS, slug(a) + ".svg")
    if os.path.exists(src) and not os.path.exists(dst): shutil.copy(src, dst)
    elif not os.path.exists(src): print("нет исходника для", a, "->", w)
