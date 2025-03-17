"""${message}.

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op
from mxr.orm import MXRDB

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: str | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}

schema=MXRDB.schema_name

def upgrade() -> None:
    """Upgrade."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade."""
    ${downgrades if downgrades else "pass"}
