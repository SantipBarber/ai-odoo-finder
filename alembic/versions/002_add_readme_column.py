"""Add readme column to odoo_modules

Revision ID: 002
Revises: 001
Create Date: 2025-11-15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Add readme column to odoo_modules table
    op.add_column('odoo_modules', sa.Column('readme', sa.Text(), nullable=True))


def downgrade():
    # Remove readme column
    op.drop_column('odoo_modules', 'readme')
