"""Add doctor_id to Patient

Revision ID: 82a043a7b219
Revises: 7eb3da5baba2
Create Date: 2025-01-23 05:11:15.454636

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82a043a7b219'
down_revision = '7eb3da5baba2'
branch_labels = None
depends_on = None


def upgrade():
    # Add the doctor_id column as nullable initially
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.add_column(sa.Column('doctor_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'doctor', ['doctor_id'], ['id'])


def downgrade():
    # Remove the foreign key and column during downgrade
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('doctor_id')
