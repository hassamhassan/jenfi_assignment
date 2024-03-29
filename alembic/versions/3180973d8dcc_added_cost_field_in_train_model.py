"""Added cost field in train model

Revision ID: 3180973d8dcc
Revises: eccd6405e6be
Create Date: 2024-01-27 08:44:37.429693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3180973d8dcc'
down_revision: Union[str, None] = 'eccd6405e6be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('trains', sa.Column('cost', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('trains', 'cost')
    # ### end Alembic commands ###
