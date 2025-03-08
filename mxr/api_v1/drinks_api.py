"""Drinks API."""

import json

from flask import Blueprint, Response, current_app, request
from sqlalchemy import select
from sqlalchemy.orm import Session

from mxr.orm import Drinks, Ingredients

drinks = Blueprint("drinks", __name__, template_folder="templates")

# TODO(Richie): make Drinks and Ingredients json serializable


def get_ingredients(drink: Drinks) -> dict[str, dict[str, str | float | None]]:
    """Get the ingredients for a drink.

    Args:
        drink (Drinks): The drink to get the ingredients for.

    Returns:
        list[dict[str, str]]: A list of dictionaries containing the ingredient name and measurement.
    """
    return {
        ingredient.name: {
            "category": ingredient.category,
            "alcohol_content": ingredient.alcohol_content,
            "measurement": measurement,
        }
        for ingredient, measurement in drink.ingredients.items()
    }


# TODO(Richie): THis doesn't support egesting ingredients
@drinks.route("/drinks", methods=["POST"])
def create_drink() -> Response:
    """Create a drink."""
    drink_data = request.get_json()

    with Session(current_app.config["ENGINE"]) as session:
        drink = Drinks(
            name=drink_data["name"],
            garnish=drink_data.get("garnish"),
            ingredients={
                Ingredients(name=ingredient["name"]): ingredient["measurement"]
                for ingredient in drink_data["ingredients"]
            },
            preparation=drink_data["preparation"],
        )
        session.add(drink)
        session.commit()
        id = drink.id

    return Response(status=201, response=json.dumps({"id": id}))


@drinks.route("/drinks")
def get_drinks() -> Response:
    """Get the drinks."""
    with Session(current_app.config["ENGINE"]) as session:
        raw_drinks = session.execute(select(Drinks)).scalars().all()

        drinks_data = json.dumps(
            [
                {
                    "id": drink.id,
                    "name": drink.name,
                    "garnish": drink.garnish,
                    "ingredients": get_ingredients(drink),
                    "preparation": drink.preparation,
                }
                for drink in raw_drinks
            ]
        )

    return Response(status=201, response=drinks_data)


@drinks.route("/drinks/<int:id>")
def get_drink(id: int) -> Response:
    """Get a drink."""
    with Session(current_app.config["ENGINE"]) as session:
        drink = session.execute(select(Drinks).where(Drinks.id == id)).scalars().one()

        return Response(
            status=201,
            response=json.dumps(
                {
                    "id": drink.id,
                    "name": drink.name,
                    "garnish": drink.garnish,
                    "ingredients": get_ingredients(drink),
                    "preparation": drink.preparation,
                }
            ),
        )


@drinks.route("/drinks/<int:id>", methods=["PUT"])
def update_drink(id: int) -> Response:
    """Update a drink."""
    drink_data = request.get_json()
    with Session(current_app.config["ENGINE"]) as session:
        drink = session.execute(select(Drinks).where(Drinks.id == id)).scalars().one()
        drink.name = drink_data.get("name", drink.name)
        drink.garnish = drink_data.get("garnish", drink.garnish)
        drink.ingredients = drink_data.get("ingredients", drink.ingredients)
        drink.preparation = drink_data.get("preparation", drink.preparation)
        session.commit()

    return Response(status=200)
