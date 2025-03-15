"""Alembic."""

from __future__ import annotations

import sys
import logging
from typing import Literal, TYPE_CHECKING

from sqlalchemy import URL, create_engine

from alembic import context
from mxr.orm import MXRDB, Drink  # noqa: F401
from mxr.common import get_url

if TYPE_CHECKING:
    from collections.abc import MutableMapping

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


target_metadata = MXRDB.metadata
logging.basicConfig(
    level="DEBUG",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def run_migrations_offline(url: URL) -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# This is part of the Alembic specification
def include_name(
    name: str | None,
    type_: Literal["schema", "table", "column", "index", "unique_constraint", "foreign_key_constraint"],
    parent_names: MutableMapping[Literal["schema_name", "table_name", "schema_qualified_table_name"], str | None],  # noqa: ARG001
) -> bool:
    """This filter table to be included in the migration.

    Args:
        name (str): The name of the table.
        type_ (str): The type of the table.
        parent_names (list[str]): The names of the parent tables.

    Returns:
        bool: True if the table should be included, False otherwise.

    """
    if type_ == "schema":
        return name == target_metadata.schema
    return True


def run_migrations_online(url: URL) -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=MXRDB.schema_name,
            include_name=include_name,
        )

        with context.begin_transaction():
            context.run_migrations()


url = get_url("MXR")


if context.is_offline_mode():
    run_migrations_offline(url)
else:
    run_migrations_online(url)
