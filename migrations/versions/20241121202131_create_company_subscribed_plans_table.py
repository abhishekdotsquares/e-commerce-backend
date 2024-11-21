"""create company_subscribed_plans table

Revision ID: 80ef934cf770
Revises: f9575657e682
Create Date: 2024-11-21 20:21:31.853022

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '80ef934cf770'
down_revision = 'f9575657e682'
branch_labels = None
depends_on = None


def upgrade():
     op.create_table(
        'company_subscribed_plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.TIMESTAMP(), nullable=False),
        sa.Column('end_date', sa.TIMESTAMP(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_company_subscribed_plans_company_id'),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], name='fk_company_subscribed_plans_plan_id'),
        sa.PrimaryKeyConstraint('id', name='company_subscribed_plans_pkey')
    )



def downgrade():
    op.drop_table('company_subscribed_plans')

    # ### end Alembic commands ###
