"""initial

Revision ID: 001
Revises: 
Create Date: 2024-01-01

"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # جداول core
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('telegram_id', sa.BigInteger(), unique=True, index=True),
        sa.Column('username', sa.String(64), nullable=True),
        sa.Column('full_name', sa.String(128)),
        sa.Column('role', sa.String(32), default='user'),
        sa.Column('is_blocked', sa.Boolean(), default=False),
        sa.Column('wallet_balance', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # wallets
    op.create_table('wallets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), unique=True),
        sa.Column('balance', sa.Float(), default=0.0),
        sa.Column('reserved_balance', sa.Float(), default=0.0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # transactions, tracks, service_plans, orders, tickets, etc. (ادامه جداول)
    # ... (مختصر شده)

def downgrade() -> None:
    op.drop_table('wallets')
    op.drop_table('users')
    # etc.
