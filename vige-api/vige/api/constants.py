from .utils import IntEnum, Enum


class BoPermission(Enum):
    misc_sensitive_info_view = 'misc_sensitive_info_view'

    # 系统级别
    live_settings_manage = 'live_settings_manage'

    # 后台用户
    bo_roles_view = 'bo_roles_view'
    bo_roles_manage = 'bo_roles_manage'
    bo_users_view = 'bo_users_view'
    bo_users_manage = 'bo_users_manage'
    bo_users_wechat_bind_manage = 'bo_users_wechat_bind_manage'

    # 账套管理
    account_set_view = 'account_set_view'
    account_set_manage = 'account_set_manage'

    # 科目管理
    account_view = 'account_view'
    account_manage = 'account_manage'

    # 凭证管理
    voucher_entry = 'voucher_entry'           # 录入
    voucher_review = 'voucher_review'        # 审核
    voucher_post = 'voucher_post'           # 过账
    voucher_delete = 'voucher_delete'        # 删除
    voucher_print = 'voucher_print'          # 打印

    # 发票管理
    invoice_view = 'invoice_view'
    invoice_manage = 'invoice_manage'

    # 财务报表
    report_view = 'report_view'
    report_export = 'report_export'

    # 税务管理
    tax_view = 'tax_view'
    tax_manage = 'tax_manage'


BoPermission.misc_sensitive_info_view.label = 'Sensitive Info View'  # '敏感用户信息 - 查看'
BoPermission.live_settings_manage.label = 'Settings Manage'  # '管理系统配置'
BoPermission.bo_roles_view.label = 'Roles View'  # '查看角色'
BoPermission.bo_roles_manage.label = 'Roles Manage'  # '管理角色'
BoPermission.bo_users_view.label = 'Users View'  # '查看用户列表'
BoPermission.bo_users_manage.label = 'Users Manage'  # '管理用户'
BoPermission.bo_users_wechat_bind_manage.label = 'Users WeChat Bind Manage'  # '管理微信账户绑定'

# 账套管理
BoPermission.account_set_view.label = 'Account Set View'  # '查看账套'
BoPermission.account_set_manage.label = 'Account Set Manage'  # '管理账套'

# 科目管理
BoPermission.account_view.label = 'Account View'  # '查看科目'
BoPermission.account_manage.label = 'Account Manage'  # '管理科目'

# 凭证管理
BoPermission.voucher_entry.label = 'Voucher Entry'  # '凭证录入'
BoPermission.voucher_review.label = 'Voucher Review'  # '凭证审核'
BoPermission.voucher_post.label = 'Voucher Post'  # '凭证过账'
BoPermission.voucher_delete.label = 'Voucher Delete'  # '凭证删除'
BoPermission.voucher_print.label = 'Voucher Print'  # '凭证打印'

# 发票管理
BoPermission.invoice_view.label = 'Invoice View'  # '查看发票'
BoPermission.invoice_manage.label = 'Invoice Manage'  # '管理发票'

# 财务报表
BoPermission.report_view.label = 'Report View'  # '查看报表'
BoPermission.report_export.label = 'Report Export'  # '导出报表'

# 税务管理
BoPermission.tax_view.label = 'Tax View'  # '查看税务'
BoPermission.tax_manage.label = 'Tax Manage'  # '管理税务'


# 绑定了后台用户的微信用户牵扯到的权限，请设置 use_in_wechat = True
# BoPermission.wechat_workbench_xxx.use_in_wechat = True


class BoPermissionGroup(IntEnum):
    system = 100
    bo_user = 200
    accounting = 300      # 账务管理
    voucher = 400         # 凭证管理
    invoice = 500         # 发票管理
    report = 600          # 报表管理
    tax = 700             # 税务管理


BoPermissionGroup.system.label = 'System'  # '系统级别'
BoPermissionGroup.bo_user.label = 'User'  # '后台用户'
BoPermissionGroup.accounting.label = 'Accounting'  # '账务管理'
BoPermissionGroup.voucher.label = 'Voucher'  # '凭证管理'
BoPermissionGroup.invoice.label = 'Invoice'  # '发票管理'
BoPermissionGroup.report.label = 'Report'  # '报表管理'
BoPermissionGroup.tax.label = 'Tax'  # '税务管理'

BoPermissionGroup.system.members = [
    BoPermission.live_settings_manage
]

BoPermissionGroup.bo_user.members = [
    BoPermission.misc_sensitive_info_view,
    BoPermission.bo_roles_view,
    BoPermission.bo_roles_manage,
    BoPermission.bo_users_view,
    BoPermission.bo_users_manage,
    BoPermission.bo_users_wechat_bind_manage,
]

BoPermissionGroup.accounting.members = [
    BoPermission.account_set_view,
    BoPermission.account_set_manage,
    BoPermission.account_view,
    BoPermission.account_manage,
]

BoPermissionGroup.voucher.members = [
    BoPermission.voucher_entry,
    BoPermission.voucher_review,
    BoPermission.voucher_post,
    BoPermission.voucher_delete,
    BoPermission.voucher_print,
]

BoPermissionGroup.invoice.members = [
    BoPermission.invoice_view,
    BoPermission.invoice_manage,
]

BoPermissionGroup.report.members = [
    BoPermission.report_view,
    BoPermission.report_export,
]

BoPermissionGroup.tax.members = [
    BoPermission.tax_view,
    BoPermission.tax_manage,
]
