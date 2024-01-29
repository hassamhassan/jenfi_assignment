"""Create initial DB tables

Revision ID: eccd6405e6be
Revises: 
Create Date: 2024-01-27 07:46:38.731896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eccd6405e6be'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('TRAIN_OPERATOR', 'PARCEL_OWNER', 'POST_MASTER', name='userrole'), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('trains',
    sa.Column('operator_id', sa.String(), nullable=False),
    sa.Column('weight_cost_factor', sa.Float(), nullable=False),
    sa.Column('volume_cost_factor', sa.Float(), nullable=False),
    sa.Column('max_weight', sa.Float(), nullable=False),
    sa.Column('max_volume', sa.Float(), nullable=False),
    sa.Column('current_weight', sa.Float(), nullable=False),
    sa.Column('current_volume', sa.Float(), nullable=False),
    sa.Column('available_lines', sa.String(), nullable=False),
    sa.Column('assigned_line', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('AVAILABLE', 'BOOKED', 'SENT', 'UNAVAILABLE', name='trainstatus'), nullable=False),
    sa.Column('departure_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parcels',
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('volume', sa.Float(), nullable=False),
    sa.Column('destination', sa.String(), nullable=False),
    sa.Column('has_shipped', sa.Boolean(), nullable=False),
    sa.Column('train_id', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['train_id'], ['trains.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('parcels')
    op.drop_table('trains')
    op.drop_table('users')
    # ### end Alembic commands ###
