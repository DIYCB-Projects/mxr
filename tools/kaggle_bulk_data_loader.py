"""Bulk data for kaggle cocktail-ingredients.

datasource https://www.kaggle.com/datasets/ai-first/cocktail-ingredients

"""

from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mxr.common import get_url
from mxr.orm import Drink, Ingredient


def main() -> None:
    """Main."""
    url = get_url("MXR")
    engine = create_engine(url)
    with (
        Path("./tools/data/all_drinks.csv").open() as csv_file,
        Session(engine) as session,
    ):
        reader = csv.DictReader(csv_file)
        for row in reader:
            raw_ingredients = (
                (row.get(f"strIngredient{num}"), row.get(f"strMeasure{num}"))
                for num in range(1, 16)
                if row.get(f"strIngredient{num}") and row.get(f"strMeasure{num}")
            )
            ingredients = {
                Ingredient.add(session, str(name)): measurement for name, measurement in raw_ingredients if name
            }

            drink = Drink(
                name=row["strDrink"],
                ingredients=ingredients,
                preparation=row["strInstructions"],
                drink_type=row["strCategory"],
                glass=row["strGlass"],
                data_source=(
                    "data_source=kaggle "
                    f"idDrink={row['idDrink']} "
                    f"strDrinkThumb={row['strDrinkThumb']} "
                    f"strAlcoholic={row['strAlcoholic']}"
                ),
            )
            session.add(drink)
            session.commit()


if __name__ == "__main__":
    main()
