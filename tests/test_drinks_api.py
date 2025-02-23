"""Test drinks API."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from mxr.orm import Drinks, Ingredients

if TYPE_CHECKING:
    from flask.testing import FlaskClient


def test_get_drinks_no_drinks(client: FlaskClient) -> None:
    """test_get_drinks_no_drinks."""
    response = client.get("/drinks")
    assert response.text == "[]"


def test_get_drinks(client: FlaskClient) -> None:
    """test_get_drinks."""
    with Session(client.application.config["ENGINE"]) as session:
        drink = Drinks(
            name="The best drink ever",
            garnish="A little umbrella",
            ingredients={Ingredients(name="love", category="sweet"), Ingredients(name="bread", category="sweet")},
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
            "ingredients": ["bread", "love"],
            "preparation": "Exuberant shaking",
        }
    ]


def test_post_drink(client: FlaskClient) -> None:
    """test_post_drink."""
    json_data = {"name": "No name", "ingredients": [{"name": "vodka"}, {"name": "xanax"}], "preparation": "shake"}
    response = client.post("/drinks", json=json_data)
    assert response.status_code == HTTPStatus.CREATED
    assert response.text == '{"id": 1}'

    with Session(client.application.config["ENGINE"]) as session:
        raw_drink = session.execute(select(Drinks).where(Drinks.id == 1)).scalars().one()
        assert raw_drink.name == "No name"
        assert {ingredient.name for ingredient in raw_drink.ingredients} == {"vodka", "xanax"}
        assert raw_drink.preparation == "shake"


def test_get_drinks_id(client: FlaskClient) -> None:
    """test_get_drinks."""
    with Session(client.application.config["ENGINE"]) as session:
        drink = Drinks(
            name="The best drink ever",
            garnish="A little umbrella",
            ingredients={Ingredients(name="love", category="sweet"), Ingredients(name="bread", category="sweet")},
            preparation="Exuberant shaking",
        )
        session.add(drink)
        session.commit()

    response = client.get("/drinks/1")
    assert json.loads(response.text) == {
        "id": 1,
        "name": "The best drink ever",
        "garnish": "A little umbrella",
        "ingredients": ["bread", "love"],
        "preparation": "Exuberant shaking",
    }


def test_update_drink(client: FlaskClient) -> None:
    """test_get_drinks."""
    with Session(client.application.config["ENGINE"]) as session:
        drink = Drinks(
            name="original",
            ingredients={Ingredients(name="nothing", category="empty")},
            preparation="test",
        )
        session.add(drink)
        session.commit()

    client.put("/drinks/1", json={"name": "old school"})

    with Session(client.application.config["ENGINE"]) as session:
        raw_drink = session.execute(select(Drinks).where(Drinks.id == 1)).scalars().one()
        assert raw_drink.name == "old school"
        assert raw_drink.ingredients.pop().name == "nothing"
        assert raw_drink.preparation == "test"
