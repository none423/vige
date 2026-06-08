"""
账务管理 API
"""
from typing import Optional
from fastapi import Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import sm
from .. import router as app
from ..bo_user.security import perm_accepted
from ..constants import BoPermission
from .models import AccountSet, Account


# ============ 表单验证 ============

class AccountSetForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description='账套名称')
    code: str = Field(..., min_length=1, max_length=50, description='账套编码')
    accounting_standard: str = Field(default='小企业会计准则', description='会计准则')
    currency: str = Field(default='CNY', description='记账本位币')


class AccountSetUpdateForm(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description='账套名称')
    accounting_standard: Optional[str] = Field(None, description='会计准则')
    currency: Optional[str] = Field(None, description='记账本位币')
    status: Optional[str] = Field(None, description='状态')
    is_default: Optional[bool] = Field(None, description='是否默认')
    current_period: Optional[str] = Field(None, description='当前会计期间')


class AccountForm(BaseModel):
    account_set_id: int = Field(..., description='所属账套')
    code: str = Field(..., min_length=1, max_length=50, description='科目编码')
    name: str = Field(..., min_length=1, max_length=100, description='科目名称')
    name_en: Optional[str] = Field(None, description='英文名称')
    direction: str = Field(..., description='方向 借/贷')
    account_type: str = Field(..., description='科目类别')
    level: int = Field(default=1, ge=1, le=5, description='科目级次')
    parent_id: Optional[int] = Field(None, description='上级科目')
    is_cash_account: bool = Field(default=False, description='现金科目')
    is_bank_account: bool = Field(default=False, description='银行科目')
    has_auxiliary: bool = Field(default=False, description='辅助核算')
    auxiliary_type: Optional[str] = Field(None, description='辅助核算类型')
    is_detail: bool = Field(default=True, description='是否最明细')
    is_used: bool = Field(default=True, description='是否启用')
    allow_manual: bool = Field(default=True, description='允许手工录入')


# ============ 账套 API ============

@app.get('/accounting/account-sets', summary='账套列表')
@perm_accepted(BoPermission.account_set_view)
def list_account_sets(
    keyword: Optional[str] = Query(None, description='搜索关键词'),
    status: Optional[str] = Query(None, description='状态'),
    db: Session = Depends(sm.get_db)
):
    """获取账套列表"""
    q = db.query(AccountSet)
    
    if keyword:
        q = q.filter(
            (AccountSet.name.ilike(f'%{keyword}%')) |
            (AccountSet.code.ilike(f'%{keyword}%'))
        )
    
    if status:
        q = q.filter(AccountSet.status == status)
    
    q = q.order_by(AccountSet.is_default.desc(), AccountSet.id)
    
    account_sets = q.all()
    return dict(
        success=True,
        rows=[s.dump() for s in account_sets]
    )


@app.get('/accounting/account-sets/{account_set_id}', summary='账套详情')
@perm_accepted(BoPermission.account_set_view)
def get_account_set(account_set_id: int, db: Session = Depends(sm.get_db)):
    """获取账套详情"""
    account_set = AccountSet.get_or_404(db, account_set_id)
    return dict(
        success=True,
        account_set=account_set.dump()
    )


@app.post('/accounting/account-sets', summary='创建账套')
@perm_accepted(BoPermission.account_set_manage)
def create_account_set(
    form: AccountSetForm,
    db: Session = Depends(sm.get_db)
):
    """创建新账套"""
    # 检查编码是否已存在
    if db.query(AccountSet).filter(AccountSet.code == form.code).first():
        raise HTTPException(status_code=400, detail='账套编码已存在')
    
    with sm.transaction_scope() as ts:
        account_set = AccountSet.create(
            ts,
            name=form.name,
            code=form.code,
            accounting_standard=form.accounting_standard,
            currency=form.currency,
            status='active',
            current_period=None
        )
    
    return dict(
        success=True,
        account_set=account_set.dump()
    )


@app.put('/accounting/account-sets/{account_set_id}', summary='更新账套')
@perm_accepted(BoPermission.account_set_manage)
def update_account_set(
    account_set_id: int,
    form: AccountSetUpdateForm,
    db: Session = Depends(sm.get_db)
):
    """更新账套信息"""
    account_set = AccountSet.get_or_404(db, account_set_id)
    
    update_data = form.dict(exclude_unset=True)
    
    # 如果设置为默认账套，先取消其他默认
    if update_data.get('is_default'):
        db.query(AccountSet).filter(
            AccountSet.is_default == True,
            AccountSet.id != account_set_id
        ).update({'is_default': False})
    
    with sm.transaction_scope():
        for key, value in update_data.items():
            setattr(account_set, key, value)
    
    return dict(
        success=True,
        account_set=account_set.dump()
    )


@app.delete('/accounting/account-sets/{account_set_id}', summary='删除账套')
@perm_accepted(BoPermission.account_set_manage)
def delete_account_set(account_set_id: int, db: Session = Depends(sm.get_db)):
    """删除账套（如果账套下有科目则不能删除）"""
    account_set = AccountSet.get_or_404(db, account_set_id)
    
    # 检查是否有科目
    account_count = db.query(Account).filter(
        Account.account_set_id == account_set_id
    ).count()
    
    if account_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f'账套下有 {account_count} 个科目，无法删除'
        )
    
    with sm.transaction_scope():
        account_set.delete()
    
    return dict(success=True, message='删除成功')


# ============ 科目 API ============

@app.get('/accounting/accounts', summary='科目列表')
@perm_accepted(BoPermission.account_view)
def list_accounts(
    account_set_id: int = Query(..., description='账套ID'),
    keyword: Optional[str] = Query(None, description='搜索关键词'),
    account_type: Optional[str] = Query(None, description='科目类别'),
    level: Optional[int] = Query(None, ge=1, le=5, description='科目级次'),
    is_used: Optional[bool] = Query(None, description='是否启用'),
    db: Session = Depends(sm.get_db)
):
    """获取科目列表"""
    q = db.query(Account).filter(Account.account_set_id == account_set_id)
    
    if keyword:
        q = q.filter(
            (Account.name.ilike(f'%{keyword}%')) |
            (Account.code.ilike(f'%{keyword}%'))
        )
    
    if account_type:
        q = q.filter(Account.account_type == account_type)
    
    if level:
        q = q.filter(Account.level == level)
    
    if is_used is not None:
        q = q.filter(Account.is_used == is_used)
    
    q = q.order_by(Account.code)
    
    accounts = q.all()
    return dict(
        success=True,
        rows=[a.dump() for a in accounts]
    )


@app.get('/accounting/accounts/tree', summary='科目树')
@perm_accepted(BoPermission.account_view)
def get_account_tree(
    account_set_id: int = Query(..., description='账套ID'),
    db: Session = Depends(sm.get_db)
):
    """获取科目树形结构"""
    accounts = db.query(Account).filter(
        Account.account_set_id == account_set_id
    ).order_by(Account.code).all()
    
    # 构建树形结构
    def build_tree(parent_id=None):
        result = []
        for acc in accounts:
            if acc.parent_id == parent_id:
                node = acc.dump()
                children = build_tree(acc.id)
                if children:
                    node['children'] = children
                result.append(node)
        return result
    
    tree = build_tree(None)
    return dict(success=True, tree=tree)


@app.get('/accounting/accounts/{account_id}', summary='科目详情')
@perm_accepted(BoPermission.account_view)
def get_account(account_id: int, db: Session = Depends(sm.get_db)):
    """获取科目详情"""
    account = Account.get_or_404(db, account_id)
    return dict(
        success=True,
        account=account.dump()
    )


@app.post('/accounting/accounts', summary='创建科目')
@perm_accepted(BoPermission.account_manage)
def create_account(
    form: AccountForm,
    db: Session = Depends(sm.get_db)
):
    """创建新科目"""
    # 验证账套存在
    account_set = AccountSet.get_or_404(db, form.account_set_id)
    
    # 检查编码是否已存在
    if db.query(Account).filter(
        Account.account_set_id == form.account_set_id,
        Account.code == form.code
    ).first():
        raise HTTPException(status_code=400, detail='科目编码已存在')
    
    # 如果有上级科目，验证存在
    if form.parent_id:
        parent = Account.get_or_404(db, form.parent_id)
        # 更新级次
        form.level = parent.level + 1
    
    with sm.transaction_scope() as ts:
        account = Account.create(
            ts,
            account_set_id=form.account_set_id,
            code=form.code,
            name=form.name,
            name_en=form.name_en,
            direction=form.direction,
            account_type=form.account_type,
            level=form.level,
            parent_id=form.parent_id,
            is_cash_account=form.is_cash_account,
            is_bank_account=form.is_bank_account,
            has_auxiliary=form.has_auxiliary,
            auxiliary_type=form.auxiliary_type,
            is_detail=form.is_detail,
            is_used=form.is_used,
            allow_manual=form.allow_manual
        )
    
    return dict(
        success=True,
        account=account.dump()
    )


@app.put('/accounting/accounts/{account_id}', summary='更新科目')
@perm_accepted(BoPermission.account_manage)
def update_account(
    account_id: int,
    form: AccountForm,
    db: Session = Depends(sm.get_db)
):
    """更新科目信息"""
    account = Account.get_or_404(db, account_id)
    
    update_data = form.dict(exclude_unset=True)
    update_data.pop('account_set_id', None)  # 不允许修改所属账套
    
    with sm.transaction_scope():
        for key, value in update_data.items():
            setattr(account, key, value)
    
    return dict(
        success=True,
        account=account.dump()
    )


@app.delete('/accounting/accounts/{account_id}', summary='删除科目')
@perm_accepted(BoPermission.account_manage)
def delete_account(account_id: int, db: Session = Depends(sm.get_db)):
    """删除科目"""
    account = Account.get_or_404(db, account_id)
    
    # 检查是否有下级科目
    child_count = db.query(Account).filter(
        Account.parent_id == account_id
    ).count()
    
    if child_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f'科目下有 {child_count} 个下级科目，无法删除'
        )
    
    with sm.transaction_scope():
        account.delete()
    
    return dict(success=True, message='删除成功')


@app.post('/accounting/account-sets/{account_set_id}/init-accounts', summary='初始化科目')
@perm_accepted(BoPermission.account_manage)
def init_accounts(
    account_set_id: int,
    accounting_standard: str = Query('小企业会计准则', description='会计准则'),
    db: Session = Depends(sm.get_db)
):
    """根据会计准则初始化标准科目"""
    account_set = AccountSet.get_or_404(db, account_set_id)
    
    # 检查是否已有科目
    existing_count = db.query(Account).filter(
        Account.account_set_id == account_set_id
    ).count()
    
    if existing_count > 0:
        raise HTTPException(
            status_code=400,
            detail='账套已有科目，请先删除现有科目'
        )
    
    # 小企业会计准则标准科目
    standard_accounts = [
        # 资产类
        {'code': '1001', 'name': '库存现金', 'type': 'asset', 'direction': '借'},
        {'code': '1002', 'name': '银行存款', 'type': 'asset', 'direction': '借'},
        {'code': '1012', 'name': '其他货币资金', 'type': 'asset', 'direction': '借'},
        {'code': '1123', 'name': '预付账款', 'type': 'asset', 'direction': '借'},
        {'code': '1122', 'name': '应收账款', 'type': 'asset', 'direction': '借'},
        {'code': '1221', 'name': '其他应收款', 'type': 'asset', 'direction': '借'},
        {'code': '1405', 'name': '库存商品', 'type': 'asset', 'direction': '借'},
        {'code': '1601', 'name': '固定资产', 'type': 'asset', 'direction': '借'},
        {'code': '1602', 'name': '累计折旧', 'type': 'asset', 'direction': '贷'},
        # 负债类
        {'code': '2001', 'name': '短期借款', 'type': 'liability', 'direction': '贷'},
        {'code': '2202', 'name': '应付账款', 'type': 'liability', 'direction': '贷'},
        {'code': '2203', 'name': '预收账款', 'type': 'liability', 'direction': '贷'},
        {'code': '2241', 'name': '其他应付款', 'type': 'liability', 'direction': '贷'},
        {'code': '2221', 'name': '应交税费', 'type': 'liability', 'direction': '贷'},
        {'code': '2501', 'name': '长期借款', 'type': 'liability', 'direction': '贷'},
        # 权益类
        {'code': '3001', 'name': '实收资本', 'type': 'equity', 'direction': '贷'},
        {'code': '3002', 'name': '资本公积', 'type': 'equity', 'direction': '贷'},
        {'code': '3101', 'name': '盈余公积', 'type': 'equity', 'direction': '贷'},
        {'code': '3103', 'name': '本年利润', 'type': 'equity', 'direction': '贷'},
        {'code': '3104', 'name': '利润分配', 'type': 'equity', 'direction': '贷'},
        # 成本类
        {'code': '4001', 'name': '生产成本', 'type': 'cost', 'direction': '借'},
        {'code': '4101', 'name': '制造费用', 'type': 'cost', 'direction': '借'},
        # 损益类
        {'code': '5001', 'name': '主营业务收入', 'type': 'profit_loss', 'direction': '贷'},
        {'code': '5051', 'name': '其他业务收入', 'type': 'profit_loss', 'direction': '贷'},
        {'code': '5401', 'name': '主营业务成本', 'type': 'profit_loss', 'direction': '借'},
        {'code': '5402', 'name': '其他业务成本', 'type': 'profit_loss', 'direction': '借'},
        {'code': '5403', 'name': '营业税金及附加', 'type': 'profit_loss', 'direction': '借'},
        {'code': '5601', 'name': '销售费用', 'type': 'profit_loss', 'direction': '借'},
        {'code': '5602', 'name': '管理费用', 'type': 'profit_loss', 'direction': '借'},
        {'code': '5603', 'name': '财务费用', 'type': 'profit_loss', 'direction': '借'},
    ]
    
    created_count = 0
    with sm.transaction_scope() as ts:
        for acc_info in standard_accounts:
            Account.create(
                ts,
                account_set_id=account_set_id,
                code=acc_info['code'],
                name=acc_info['name'],
                direction=acc_info['direction'],
                account_type=acc_info['type'],
                level=1,
                is_detail=True,
                is_used=True,
                allow_manual=True
            )
            created_count += 1
    
    return dict(
        success=True,
        message=f'成功创建 {created_count} 个标准科目',
        count=created_count
    )
