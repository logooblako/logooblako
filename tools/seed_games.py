# -*- coding: utf-8 -*-
import os, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def md(name, fm, body=""):
    p = os.path.join(ROOT, "content", name); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf8").write("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + body.strip() + "\n")
pic = lambda s: f"/assets/pics/{s}.svg"
C = lambda text="", p="", back="", group="", options="": dict(text=text, pic=p, back=back, group=group, options=options)
md("games/s-ili-sh.md", dict(title="С или Ш?", template="sort", order=1, description="Разложи картинки: где звук [С], а где [Ш].", groups="С, Ш",
   cards=[C("сок",pic("sok"),group="С"),C("сумка",pic("sumka"),group="С"),C("собака",pic("sobaka"),group="С"),C("нос",pic("nos"),group="С"),
          C("шарик",pic("sharik"),group="Ш"),C("кошка",pic("koshka"),group="Ш"),C("мышь",pic("mysh"),group="Ш"),C("груша",pic("grusha"),group="Ш")]))
md("games/gde-zhivet-zvuk-r.md", dict(title="Где звук [Р]?", template="quiz", order=2, description="Назови картинку и выбери, где звук [Р]: в начале, в середине или в конце слова.", groups="",
   cards=[C("рыба",pic("ryba"),"в начале","", "в середине, в конце"),C("корова",pic("korova"),"в середине","","в начале, в конце"),
          C("комар",pic("komar"),"в конце","","в начале, в середине"),C("ракета",pic("raketa"),"в начале","","в середине, в конце"),
          C("помидор",pic("pomidor"),"в конце","","в начале, в середине"),C("гора",pic("gora"),"в середине","","в начале, в конце")]))
md("games/pary-zhivotnye.md", dict(title="Найди пару", template="pairs", order=3, description="Открывай карточки и ищи одинаковые картинки. Называй каждую вслух!", groups="",
   cards=[C("кошка",pic("koshka")),C("собака",pic("sobaka")),C("корова",pic("korova")),C("коза",pic("koza")),C("лиса",pic("lisa")),C("слон",pic("slon"))]))
md("games/koleso-skorogovorok.md", dict(title="Колесо скороговорок", template="wheel", order=4, description="Крути колесо и повтори скороговорку, которая выпадет.", groups="",
   cards=[C("Шла Саша по шоссе и сосала сушку."),C("На дворе трава, на траве дрова."),C("Жужжит жужелица, жужжит, да не кружится."),
          C("Карл у Клары украл кораллы."),C("Мыла Мила мишку мылом."),C("Цыплёнок цапли цепко цеплялся за цепь.")]))
md("games/kto-chto-est.md", dict(title="Кто что любит?", template="flip", order=5, description="Назови животное, а потом переверни карточку: что оно любит есть?", groups="",
   cards=[C("белка",pic("belka"),"орехи"),C("кошка",pic("koshka"),"молоко"),C("ёж",pic("yozh"),"яблоки и грибы"),C("обезьяна",pic("obezyana"),"бананы"),C("корова",pic("korova"),"траву")]))
md("games/zvuk-sh-prezentaciya.md", dict(title="Знакомимся со звуком [Ш]", template="slides", order=6, description="Короткая презентация для занятия.", groups="",
   cards=[C("Звук [Ш]", pic("lyagushka"), "Шипит, как змея: ш-ш-ш. Губы — «рупором», язык — «чашечкой»."),
          C("Ш в начале слова", pic("sharik"), "Шарик, шорты, шляпа, шоколад."),
          C("Ш в середине слова", pic("koshka"), "Кошка, мишка, груша, машина."),
          C("Ш в конце слова", pic("mysh"), "Мышь, малыш, карандаш, душ.")]))
md("pages/tales-intro.md", dict(title="Терапевтические сказки"),
   "Сказки, которые помогают ребёнку пережить трудные чувства: страх, обиду, ревность, расставание, первый день в саду. Читайте вместе, не торопитесь, а после сказки спросите ребёнка, что он почувствовал и что бы сделал на месте героя.")
print("ok")
