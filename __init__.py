import gzip
import json
import os
from datetime import datetime, timedelta

import requests
from unidecode import unidecode


class MTGJSON:
    def __init__(self) -> None:
        self.allcards = "https://mtgjson.com/api/v5/AtomicCards.json.gz"
        self.allsets = "https://mtgjson.com/api/v5/SetList.json.gz"

    @staticmethod
    def control(wanted: str, path: str):
        mtgjson = MTGJSON()
        url = (
            mtgjson.allcards
            if wanted == "cards"
            else mtgjson.allsets if wanted == "sets" else None
        )

        if not os.path.isfile(path) or mtgjson._file_older_than(path, 7):
            mtgjson._download(url, path)

    def _file_older_than(self, filepath: str, age: int):
        file_timestamp = os.path.getmtime(filepath)
        file_timestamp = datetime.fromtimestamp(file_timestamp)
        current_time = datetime.now()
        return (current_time - file_timestamp) > timedelta(days=age)

    def _download(self, link: str, filepath: str):
        response = requests.get(link, stream=True)
        with open(filepath, "wb") as file:
            file.write(response.content)


class CardDatabase:
    def __init__(self) -> None:
        self._filepath = "mtgdc_carddata/AtomicCards.json.gz"
        MTGJSON.control("cards", self._filepath)
        self.atomic_cards = json.load(gzip.open(self._filepath))["data"]
        self._clean_keys = {
            self._remove_accents(card): card for card in self.atomic_cards.keys()
        }
        self.commanders_list = sorted(
            list(
                set(
                    [
                        card_name
                        for _, card_name in self._clean_keys.items()
                        if self.is_commander(self.atomic_cards[card_name][0])
                    ]
                )
            )
        )
        self.sets = SetDatabase()

    def card(self, card_name: str) -> dict:
        if card_name in self.atomic_cards.keys():
            return self.atomic_cards[card_name][0]
        return self._card(card_name)

    def _card(self, card_name: str) -> dict:
        card_name = card_name.replace("&amp;", "")
        card_name = self._remove_accents(card_name)

        if card_name in self._clean_keys.keys():
            return self.atomic_cards[self._clean_keys[card_name]][0]

        possible_keys = [
            value
            for key, value in self._clean_keys.items()
            if key.startswith(card_name) and " // " in value
        ]

        if len(possible_keys) == 1:
            return self.atomic_cards[possible_keys[0]][0]

        return {"message": "Card not found"}

    def firstprint(self, card_name) -> datetime:
        return datetime.strptime(
            self.sets.set(self.card(card_name)["firstPrinting"])["releaseDate"],
            "%Y-%m-%d",
        )

    def has_been_commander(self, card) -> bool:
        if type(card) == str:
            card = self.card(card)

        if card["name"].startswith("A-"):
            return False

        if "leadershipSkills" not in card.keys():
            return False

        if not card["leadershipSkills"]["commander"]:
            return False

        return True

    def is_commander(self, card) -> bool:
        if type(card) == str:
            card = self.card(card)

        if not self.has_been_commander(card):
            return False

        if (
            "duel" in card["legalities"].keys()
            and card["legalities"]["duel"] == "Restricted"
        ):
            return False

        return True

    def str_command_zone(
        self,
        commander: list,
        concat_symbol: str = "++",
        excluded_types: dict = {"Stickers", "Attraction"},
    ):
        try:
            filtered_cards = [
                card
                for card in commander
                if card != "Unknown Card"
                and not any(
                    c_type in self.card(card)["type"] for c_type in excluded_types
                )
            ]
            return concat_symbol.join(sorted(filtered_cards))

        except KeyError:
            return "Unknown Command Zone"

    def _remove_accents(self, input_str):
        return "".join(char for char in unidecode(input_str) if char.isalpha()).lower()


class SetDatabase:
    def __init__(self) -> None:
        self._filepath = "mtgdc_carddata/AllSets.json.gz"
        MTGJSON.control("sets", self._filepath)
        json_file = json.load(gzip.open(self._filepath))["data"]

        self.allsets = {}
        for set in json_file:
            self.allsets[set["code"]] = set

    def set(self, code):
        return self.allsets[code]


class DecklistBuilder:
    def __init__(self) -> None:
        self.database = CardDatabase()
        self.ordre = {
            "Land": 0,
            "Creature": 1,
            "Planeswalker": 2,
            "Instant": 3,
            "Sorcery": 4,
            "Artifact": 5,
            "Enchantment": 6,
            "Battle": 7,
            "Tribal": 10,
        }
        self.decklist = {
            "Creature": [],
            "Planeswalker": [],
            "Instant": [],
            "Sorcery": [],
            "Artifact": [],
            "Enchantment": [],
            "Battle": [],
            "Land": [],
        }

    @staticmethod
    def build_deck(cards_list: dict):
        self = DecklistBuilder()
        for card, qty in cards_list.items():
            types = self.database.card(card)["types"]
            lowest_type = min([self.ordre[item] for item in types])
            self.decklist[{v: k for k, v in self.ordre.items()}[lowest_type]].append(
                f"{qty} {card}"
            )

        tmp = ""
        for key in self.decklist.keys():
            if self.decklist[key]:
                qty = sum(
                    [
                        int("".join(filter(str.isdigit, line)))
                        for line in self.decklist[key]
                    ]
                )
                if key == "Sorcery":
                    tmp += f"\n// Sorceries ({qty})\n"
                else:
                    tmp += f"\n// {key}s ({qty})\n"
                tmp += "\n".join(sorted(self.decklist[key]))
                tmp += "\n"

        return tmp
