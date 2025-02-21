"""changed data type to float in menuitems

Revision ID: 4acaacd34365
Revises: d31b46028a5c
Create Date: 2025-02-21 22:17:38.832904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4acaacd34365'
down_revision = 'd31b46028a5c'
branch_labels = None
depends_on = None


def upgrade():
    # Explicitly cast total_price column to double precision (float)
    op.alter_column('orderitem', 'total_price',
                    type_=sa.Float(),
                    existing_type=sa.Integer(),
                    postgresql_using='total_price::double precision')

def downgrade():
    # Revert the column type back to Integer (if needed)
    op.alter_column('orderitem', 'total_price',
                    type_=sa.Integer(),
                    existing_type=sa.Float())


    # ### end Alembic commands ###
