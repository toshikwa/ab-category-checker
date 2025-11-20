import json
import os
from pathlib import Path
import time
from typing import Sequence

from dotenv import load_dotenv
from pydantic import BaseModel

from bwsapi.operations import get_refinements

load_dotenv()


def save_models_to_json(models: Sequence[BaseModel], filename: str, output_dir: Path) -> None:
    data = [model.model_dump() for model in models]
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    user_email = os.environ["BWS_API_USER_EMAIL"]

    # Get categories
    print("Fetching categories...")
    refinements = get_refinements(user_email=user_email)
    categories = refinements.categories
    save_models_to_json(categories, "categories.json", output_dir)
    print(f"Number of categories: {len(categories)}")

    # Get subcategories for each category
    for i, category in enumerate(categories, 1):
        time.sleep(2)
        print(f"[{i}/{len(categories)}] Fetching subcategories for {category.display_name}...")
        refinements = get_refinements(user_email=user_email, category=category.id)
        sub_categories = refinements.sub_categories
        save_models_to_json(sub_categories, f"{category.id}.json", output_dir)
        print(f"  → Number of subcategories: {len(sub_categories)}")


if __name__ == "__main__":
    main()
