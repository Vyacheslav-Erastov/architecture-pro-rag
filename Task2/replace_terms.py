import json
import os
import re
from pathlib import Path

KNOWLEDGE_BASE_DIR = Path("knowledge_base")
TERMS_MAP_PATH = Path("terms_map.json")


def load_terms_map():
    with open(TERMS_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_regex(term: str) -> re.Pattern:
    escaped = re.escape(term)

    pattern = rf"""
        (?:
            (?<![a-zA-Z])
            | (?<=[A-Z])
            | ^         
        )
        {escaped}
        (?:
            (?![a-zA-Z])
            | (?=[A-Z])
            | $
        )
    """

    return re.compile(pattern, re.IGNORECASE | re.VERBOSE)


def replace_terms_in_text(text: str, terms_map: dict) -> str:
    sorted_terms = sorted(terms_map.items(), key=lambda x: len(x[0]), reverse=True)

    for original, replacement in sorted_terms:
        regex = build_regex(original)
        text = regex.sub(replacement, text)

    return text


def process_file(file_path: Path, terms_map: dict):
    original_text = file_path.read_text(encoding="utf-8")
    replaced_text = replace_terms_in_text(original_text, terms_map)
    file_path.write_text(replaced_text, encoding="utf-8")
    old_filename = file_path.stem
    new_filename = old_filename
    sorted_terms = sorted(terms_map.items(), key=lambda x: len(x[0]), reverse=True)
    for original, replacement in sorted_terms:
        if original.lower() in old_filename.replace("_", " ").lower():
            new_filename = replacement.replace(" ", "_").lower()
            break
    file_path.rename(os.path.join(os.path.split(str(file_path))[0], f"{new_filename}.md"))
    print(f"Updated: {file_path}")


def main():
    terms_map = load_terms_map()

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*.md"):
        process_file(file_path, terms_map)


if __name__ == "__main__":
    main()
