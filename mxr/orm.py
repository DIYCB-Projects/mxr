"""ORM."""

from __future__ import annotations

import logging

# This is required because datetime is required during runtime fro sqlalchemy
from datetime import datetime  # noqa: TC003
from os import getenv
from typing import Self

from sqlalchemy import ForeignKey, Index, MetaData, String, UniqueConstraint, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, object_session, relationship
from sqlalchemy.orm.collections import attribute_keyed_dict

from mxr.common import utc_now


def get_object_session(instance: object) -> Session:
    """Return the session bound to the given object.

    Args:
        instance: The object to get the session for.

    Returns:
        The session bound to the object.

    Raises:
        RuntimeError: If the object is not bound to a session.
    """
    if session := object_session(instance):
        return session
    error = f"Object {instance} is not bound to a session"
    raise RuntimeError(error)


class MXRDB(DeclarativeBase):
    """Base class for all models."""

    schema_name = getenv("MXR_SCHEMA", "mxr")

    metadata = MetaData(schema=schema_name)


class IdTimestampColumns:
    """Mixin for models that have an id and timestamp columns."""

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(onupdate=utc_now, default=utc_now)


class TableBase(IdTimestampColumns, AbstractConcreteBase, MXRDB):
    """Base class for all tables."""


class LookupTableMixin:
    """A lookup table."""

    __table_args__ = (UniqueConstraint("name"),)

    name: Mapped[str]

    def __init__(self, name: str) -> None:
        """Init."""
        self.name = name

    @classmethod
    def get(class_, session: Session, name: str) -> Self | None:
        """Get a lookup table by name.

        Args:
            name (str): The name of the lookup table.
            session (Session): The sqlalchemy session to use.

        Returns:
            BaseLookupTable | None`: The lookup table, or None if not found.
        """
        return session.scalars(select(class_).where(class_.name == name)).one_or_none()

    @classmethod
    def add(class_, session: Session, name: str) -> Self:
        """Add a lookup table.

        Args:
            name (str): The name of the lookup table.
            session (Session): The sqlalchemy session to use.

        Returns:
            BaseLookupTable: The lookup table.
        """
        if item := class_.get(session, name):
            return item

        try:
            item = class_(name=name)
            session.add(item)
            session.commit()
        except IntegrityError:
            if item := class_.get(session, name):
                msg = f"Duplicate item in lookup table {name}"
                logging.info(msg)
                return item
            raise
        return item


class Drink(TableBase):
    """Table for drinks."""

    __tablename__ = "drinks"

    # fmt: off

    name:            Mapped[str]
    preparation:     Mapped[str]
    alcohol_content: Mapped[float | None]
    data_source:     Mapped[str | None]
    drink_type:      Mapped[str | None]
    garnish:         Mapped[str | None]
    glass:           Mapped[str | None]

    # fmt: on

    drinks_ingredients_associations: Mapped[dict[Ingredient, DrinkIngredientAssociation]] = relationship(
        "DrinkIngredientAssociation",
        back_populates="drink",
        collection_class=attribute_keyed_dict("ingredient"),
        cascade="all, delete-orphan",
    )

    ingredients: AssociationProxy[dict[Ingredient, str]] = association_proxy(
        "drinks_ingredients_associations",
        "measurement",
        creator=lambda ingredient_obj, measurement_str: DrinkIngredientAssociation(
            ingredient=ingredient_obj,
            measurement=measurement_str,
        ),
    )


class Ingredient(LookupTableMixin, TableBase):
    """Table for ingredients."""

    __tablename__ = "ingredients"

    def __init__(
        self,
        name: str,
        alcohol_content: float | None = None,
        category: str | None = None,
    ) -> None:
        """Init."""
        self.alcohol_content = alcohol_content
        self.category = category
        super().__init__(name)

    # fmt: off

    alcohol_content:   Mapped[float | None]
    category:          Mapped[str | None]

    # fmt: on


class DrinkIngredientAssociation(TableBase):
    """DrinkIngredientAssociation."""

    __tablename__ = "drink_ingredient_associations"
    __table_args__ = (
        UniqueConstraint("drinks_id", "ingredients_id"),
        Index("drinks_id", "drinks_id"),
        Index("ingredients_id", "ingredients_id"),
    )

    # fmt: off

    drinks_id:      Mapped[int] = mapped_column(ForeignKey("drinks.id"))
    ingredients_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    measurement:    Mapped[str] = mapped_column(String(50))

    drink:          Mapped[Drink] = relationship(back_populates="drinks_ingredients_associations")

    ingredient:     Mapped[Ingredient] = relationship()

    # fmt: off
