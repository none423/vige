"""Add account_sets and accounts tables

Revision ID: xxxxxxxx
Revises: 
Create Date: 2026-06-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'xxxxxxxx'
down_revision = None  # 替换为当前最新的 migration hash
branch_labels = None
depends_on = None


def upgrade():
    # 创建账套表
    op.create_table(
        'account_sets',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('profile', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='账套名称'),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True, comment='账套编码'),
        sa.Column('accounting_standard', sa.String(length=50), nullable=True, server_default='小企业会计准则', comment='会计准则'),
        sa.Column('currency', sa.String(length=10), nullable=True, server_default='CNY', comment='记账本位币'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active', comment='状态'),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false', comment='是否默认账套'),
        sa.Column('current_period', sa.String(length=7), nullable=True, comment='当前会计期间'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_account_sets_code', 'account_sets', ['code'])
    op.create_index('idx_account_sets_status', 'account_sets', ['status'])

    # 创建会计科目表
    op.create_table(
        'accounts',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('profile', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('account_set_id', sa.BigInteger(), nullable=False, comment='所属账套'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='科目编码'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='科目名称'),
        sa.Column('name_en', sa.String(length=100), nullable=True, comment='英文名称'),
        sa.Column('direction', sa.String(length=10), nullable=False, comment='方向 借/贷'),
        sa.Column('account_type', sa.String(length=50), nullable=False, comment='科目类别'),
        sa.Column('level', sa.Integer(), nullable=True, server_default='1', comment='科目级次'),
        sa.Column('parent_id', sa.BigInteger(), nullable=True, comment='上级科目'),
        sa.Column('is_cash_account', sa.Boolean(), nullable=True, server_default='false', comment='现金科目'),
        sa.Column('is_bank_account', sa.Boolean(), nullable=True, server_default='false', comment='银行科目'),
        sa.Column('has_auxiliary', sa.Boolean(), nullable=True, server_default='false', comment='辅助核算'),
        sa.Column('auxiliary_type', sa.String(length=50), nullable=True, comment='辅助核算类型'),
        sa.Column('is_detail', sa.Boolean(), nullable=True, server_default='true', comment='是否最明细科目'),
        sa.Column('is_used', sa.Boolean(), nullable=True, server_default='true', comment='是否启用'),
        sa.Column('allow_manual', sa.Boolean(), nullable=True, server_default='true', comment='允许手工录入'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0', comment='排序'),
        sa.ForeignKeyConstraint(['account_set_id'], ['account_sets.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_accounts_set', 'accounts', ['account_set_id'])
    op.create_index('idx_accounts_code', 'accounts', ['code'])
    op.create_index('idx_accounts_parent', 'accounts', ['parent_id'])
    op.create_index('idx_accounts_type', 'accounts', ['account_type'])


def downgrade():
    op.drop_table('accounts')
    op.drop_table('account_sets')
