"""
会计账套和科目模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Unicode,
    Text,
    Column,
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean,
    Date,
    JSON
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    Session
)

from ...db import Base, CRUDMixin, ProfileMixin


class AccountSet(CRUDMixin, ProfileMixin):
    """
    会计账套
    支持多账套，每个账套对应一个独立的会计核算体系
    """
    __tablename__ = 'account_sets'

    # 基础信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment='账套名称')
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment='账套编码')
    
    # 会计准则
    accounting_standard: Mapped[str] = mapped_column(
        String(50), 
        default='小企业会计准则',
        comment='会计准则'
    )
    currency: Mapped[str] = mapped_column(
        String(10), 
        default='CNY',
        comment='记账本位币'
    )
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        default='active',
        comment='状态 active/inactive'
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, 
        default=False,
        comment='是否默认账套'
    )
    
    # 期间管理
    current_period: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
        comment='当前会计期间 YYYY-MM'
    )
    
    # 审计字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow
    )

    def dump(self):
        return dict(
            id=self.id,
            name=self.name,
            code=self.code,
            accounting_standard=self.accounting_standard,
            currency=self.currency,
            status=self.status,
            is_default=self.is_default,
            current_period=self.current_period,
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None,
        )


class Account(CRUDMixin, ProfileMixin):
    """
    会计科目
    支持多级科目，遵循小企业会计准则
    """
    __tablename__ = 'accounts'

    account_set_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('account_sets.id'),
        nullable=False,
        index=True,
        comment='所属账套'
    )
    
    # 科目属性
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment='科目编码'
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='科目名称'
    )
    name_en: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment='英文名称'
    )
    
    # 科目分类
    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment='方向 借/贷'
    )
    account_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='科目类别 asset/liability/equity/cost/profit_loss'
    )
    
    # 科目级次
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment='科目级次 1-5'
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('accounts.id'),
        nullable=True,
        index=True,
        comment='上级科目'
    )
    
    # 辅助核算
    is_cash_account: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='现金科目'
    )
    is_bank_account: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='银行科目'
    )
    has_auxiliary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='辅助核算'
    )
    auxiliary_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment='辅助核算类型 department/project/customer/supplier'
    )
    
    # 控制
    is_detail: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment='是否最明细科目'
    )
    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment='是否启用'
    )
    allow_manual: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment='允许手工录入'
    )
    
    # 排序
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment='排序'
    )

    def dump(self, with_children=False):
        data = dict(
            id=self.id,
            account_set_id=self.account_set_id,
            code=self.code,
            name=self.name,
            name_en=self.name_en,
            direction=self.direction,
            account_type=self.account_type,
            level=self.level,
            parent_id=self.parent_id,
            is_cash_account=self.is_cash_account,
            is_bank_account=self.is_bank_account,
            has_auxiliary=self.has_auxiliary,
            auxiliary_type=self.auxiliary_type,
            is_detail=self.is_detail,
            is_used=self.is_used,
            allow_manual=self.allow_manual,
            sort_order=self.sort_order,
        )
        return data
