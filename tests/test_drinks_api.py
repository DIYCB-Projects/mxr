"""Test drinks API."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from mxr.orm import Drink, Ingredient

if TYPE_CHECKING:
    from flask.testing import FlaskClient


def test_get_drinks_no_drinks(client: FlaskClient) -> None:
    """test_get_drinks_no_drinks."""
    response = client.get("/drinks")
    assert response.text == "[]"


def test_get_drinks(client: FlaskClient) -> None:
    """test_get_drinks."""
    with Session(client.application.config["ENGINE"]) as session:
        drink = Drink(
            name="The best drink ever",
            garnish="A little umbrella",
            ingredients={
                Ingredient(name="love", category="sweet"): "1 ML",
                Ingredient(name="bread", category="sweet"): "100 ML",
            },
            preparation="Exuberant shaking",
        )
        session.add(drink)
        session.commit()

    response = client.get("/drinks")
    assert json.loads(response.text) == [
        {
            "id": 1,
            "name": "The best drink ever",
            "garnish": "A little umbrella",
            "ingredients": {
                "bread": {"category": "sweet", "alcohol_content": None, "measurement": "100 ML"},
                "love": {"category": "sweet", "alcohol_content": None, "measurement": "1 ML"},
            },
            "preparation": "Exuberant shaking",
        }
    ]


def test_post_drink(client: FlaskClient) -> None:
    """test_post_drink."""
    json_data = {
        "name": "No name",
        "ingredients": [
            {"name": "vodka", "measurement": "1 ML"},
            {"name": "xanax", "measurement": "100 ML"},
        ],
        "preparation": "shake",
    }
    response = client.post("/drinks", json=json_data)
    assert response.text == '{"id": 1}'
    assert response.status_code == HTTPStatus.CREATED

    with Session(client.application.config["ENGINE"]) as session:
        raw_drink = session.execute(select(Drink).where(Drink.id == 1)).scalars().one()
        assert raw_drink.name == "No name"
        assert {ingredient.name: measurement for ingredient, measurement in raw_drink.ingredients.items()} == {
            "vodka": "1 ML",
            "xanax": "100 ML",
        }
        assert raw_drink.preparation == "shake"


def test_get_drinks_id(client: FlaskClient) -> None:
    """test_get_drinks."""
    with Session(client.application.config["ENGINE"]) as session:
        drink = Drink(
            name="The best drink ever",
            garnish="A little umbrella",
            ingredients={
                Ingredient(name="love", category="sweet"): "1 ML",
                Ingredient(name="bread", category="sweet"): "100 ML",
            },
            preparation="Exuberant shaking",
        )
        session.add(drink)
        session.commit()

    response = client.get("/drinks/1")
    assert json.loads(response.text) == {
        "id": 1,
        "name": "The best drink ever",
        "garnish": "A little umbrella",
        "ingredients": {
            "bread": {"category": "sweet", "alcohol_content": None, "measurement": "100 ML"},
            "love": {"category": "sweet", "alcohol_content": None, "measurement": "1 ML"},
        },
        "preparation": "Exuberant shaking",
    }


def test_update_drink(client: FlaskClient) -> None:
    """test_get_drinks."""
    with Session(client.application.config["ENGINE"]) as session:
        drink = Drink(
            name="original",
            ingredients={Ingredient(name="nothing", category="empty"): "0 grams"},
            preparation="test",
        )
        session.add(drink)
        session.commit()

    client.put("/drinks/1", json={"name": "old school"})

    with Session(client.application.config["ENGINE"]) as session:
        raw_drink = session.execute(select(Drink).where(Drink.id == 1)).scalars().one()
        assert raw_drink.name == "old school"
        assert {ingredient.name: measurement for ingredient, measurement in raw_drink.ingredients.items()} == {
            "nothing": "0 grams"
        }
        assert raw_drink.preparation == "test"
