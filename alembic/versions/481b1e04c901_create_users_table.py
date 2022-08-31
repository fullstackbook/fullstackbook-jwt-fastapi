"""create users table

Revision ID: 481b1e04c901
Revises: 
Create Date: 2022-08-30 20:56:35.188712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '481b1e04c901'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    create table users (
        id serial primary key,
        username text not null unique,
        email text not null unique,
        password text
    );
    """)


def downgrade() -> None:
    op.execute("drop table users;")
