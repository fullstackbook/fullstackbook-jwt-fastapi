"""create roles table

Revision ID: 9ce62b651a8f
Revises: 481b1e04c901
Create Date: 2022-08-31 21:02:10.601736

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ce62b651a8f'
down_revision = '481b1e04c901'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    create table roles (
        id serial primary key,
        name text not null unique
    );
    """)


def downgrade() -> None:
    op.execute("drop table roles;")
