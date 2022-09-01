"""create users_to_roles table

Revision ID: 2d8360fae38a
Revises: 9ce62b651a8f
Create Date: 2022-08-31 21:02:25.266259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d8360fae38a'
down_revision = '9ce62b651a8f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    create table users_to_roles (
        user_id int references users (id),
        role_id int references roles (id)
    );
    """)


def downgrade() -> None:
    op.execute("drop table users_to_roles;")
