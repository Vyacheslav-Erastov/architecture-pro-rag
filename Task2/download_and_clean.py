import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://starwars.fandom.com/wiki/"

ENTITIES = {
    "characters": [
        "Darth_Vader", "Luke_Skywalker", "Leia_Organa", "Obi-Wan_Kenobi",
        "Emperor_Palpatine", "Yoda", "Anakin_Skywalker", "Han_Solo",
        "Boba_Fett", "Mace_Windu", "Padmé_Amidala", "Grand_Moff_Tarkin"
    ],
    "planets": [
        "Tatooine", "Coruscant", "Naboo", "Endor",
        "Mustafar", "Hoth", "Dagobah", "Alderaan"
    ],
    "technology": [
        "Death_Star", "Lightsaber", "Hyperdrive",
        "Star_Destroyer", "TIE_fighter", "X-wing_starfighter"
    ],
    "organizations": [
        "Jedi_Order", "Sith", "Galactic_Empire", "Rebel_Alliance"
    ],
    "events": [
        "Clone_Wars", "Order_66", "The_Force", "Galactic_Senate"
    ]
}


def clean_text(text: str) -> str:
    text = re.sub(r"\[\d+]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_article_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    content = soup.find("div", {"class": "mw-parser-output"})
    if not content:
        return ""

    paragraphs = content.find_all("p", recursive=False)

    texts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 50:
            texts.append(clean_text(text))

    return "\n\n".join(texts)


def save_article(category: str, title: str, text: str):
    dir_path = Path("knowledge_base") / category
    dir_path.mkdir(parents=True, exist_ok=True)

    file_name = title.lower().replace(" ", "_") + ".md"
    file_path = dir_path / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# {title.replace('_', ' ')}\n\n")
        f.write(text)

    print(f"Saved: {file_path}")


def download_entity(category: str, entity: str):
    url = BASE_URL + entity
    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        print(f"Failed to fetch {entity}")
        return

    article_text = extract_article_text(response.text)

    if not article_text:
        print(f"Empty article: {entity}")
        return

    save_article(category, entity, article_text)


def main():
    for category, entities in ENTITIES.items():
        for entity in entities:
            download_entity(category, entity)


if __name__ == "__main__":
    main()