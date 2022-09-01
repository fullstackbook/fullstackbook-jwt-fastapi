"""insert roles

Revision ID: ece871602084
Revises: 2d8360fae38a
Create Date: 2022-08-31 21:05:14.000853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ece871602084'
down_revision = '2d8360fae38a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    insert into roles (name) values ('ROLE_USER');
    insert into roles (name) values ('ROLE_MODERATOR');
    insert into roles (name) values ('ROLE_ADMIN');
    """)


def downgrade() -> None:
    op.execute("""
    delete from roles where name in ('ROLE_USER', 'ROLE_MODERATOR', 'ROLE_ADMIN');
    """)
