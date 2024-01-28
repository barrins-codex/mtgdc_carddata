import json

from mtgdc_carddata import CardDatabase, SetDatabase

database = CardDatabase()
sets = SetDatabase()

if __name__ == "__main__":
    with open("mtgdc_carddata/sticker.json", "w", encoding="utf-8") as file:
        json.dump(
            database.card("Ancestral / Hot Dog / Minotaur"),
            file,
            ensure_ascii=False,
            indent=4,
        )

    with open("mtgdc_carddata/attraction.json", "w", encoding="utf-8") as file:
        json.dump(database.card("Balloon Stand"), file, ensure_ascii=False, indent=4)

    with open("mtgdc_carddata/background.json", "w", encoding="utf-8") as file:
        json.dump(
            database.card("Agent of the Iron Throne"),
            file,
            ensure_ascii=False,
            indent=4,
        )

    with open("mtgdc_carddata/companion.json", "w", encoding="utf-8") as file:
        json.dump(
            database.card("Lurrus of the Dream-Den"), file, ensure_ascii=False, indent=4
        )

    with open("mtgdc_carddata/sheoldred.json", "w", encoding="utf-8") as file:
        json.dump(database.card("Sheoldred"), file, ensure_ascii=False, indent=4)

    with open("mtgdc_carddata/fireice.json", "w", encoding="utf-8") as file:
        json.dump(database.card("Fire / Ice"), file, ensure_ascii=False, indent=4)

    with open("mtgdc_carddata/card.json", "w", encoding="utf-8") as file:
        json.dump(database.card("Counterspell"), file, ensure_ascii=False, indent=4)

    with open("mtgdc_carddata/set.json", "w", encoding="utf-8") as file:
        json.dump(sets.set("LCI"), file, ensure_ascii=False, indent=4)

    with open("mtgdc_carddata/yuriko.json", "w", encoding="utf-8") as file:
        json.dump(
            database.card("Yuriko, the Tiger's Shadow"),
            file,
            ensure_ascii=False,
            indent=4,
        )
