"""attribute unique was added

Revision ID: 67f948587e63
Revises: 
Create Date: 2023-04-16 13:59:17.934506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67f948587e63'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'admins', ['login_id'])
    op.create_unique_constraint(None, 'categories', ['title'])
    op.create_unique_constraint(None, 'clients', ['login_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'clients', type_='unique')
    op.drop_constraint(None, 'categories', type_='unique')
    op.drop_constraint(None, 'admins', type_='unique')
    # ### end Alembic commands ###