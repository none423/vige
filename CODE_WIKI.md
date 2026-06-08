# Vige 项目 Code Wiki

## 目录
1. [项目概述](#项目概述)
2. [技术架构](#技术架构)
3. [项目结构](#项目结构)
4. [核心模块详解](#核心模块详解)
5. [数据库模型](#数据库模型)
6. [API 接口规范](#api-接口规范)
7. [前端架构](#前端架构)
8. [配置与部署](#配置与部署)
9. [开发指南](#开发指南)

---

## 项目概述

### 项目简介
Vige（维格）是一个基于 FastAPI + Vue 的一体化工程模板，包含后端 API、前台 Web、后台管理与微信 H5 客户端，内置认证、任务队列、国际化、媒体上传与统一的 API 规范，适合作为中小型项目的起步框架。

### 主要特性
- 模块化 FastAPI 后端（users、media、settings、wechat 等）
- JWT + Cookie 认证与 CSRF 防护，统一前缀 `/v1`
- Redis + Huey 异步任务队列（环境可配置）
- PostgreSQL（SQLAlchemy 2.0）+ Alembic 数据迁移
- i18n（Babel），Makefile 常用脚本
- 媒体上传与静态挂载 `/media`
- 三套前端：Web（iView）、Admin（iView）、WeChat H5（Mint UI）
- 统一 axios 拦截器，响应结构 `{ success, data, message }`

---

## 技术架构

### 后端技术栈
- **框架**: FastAPI 0.115.6
- **ORM**: SQLAlchemy 2.0.8
- **数据库迁移**: Alembic 1.14.0
- **异步任务**: Huey 2.5.0
- **缓存**: Redis 2.10.6
- **认证**: async-fastapi-jwt-auth 0.6.6
- **数据库**: PostgreSQL 14
- **Python 版本**: 3.10
- **Web 服务器**: Uvicorn 0.34.0

### 前端技术栈
- **框架**: Vue 2.x
- **UI 组件库**:
  - 管理后台 (vige-bo): iView 3.x
  - 前台 (vige-web): iView 3.x
  - 微信 H5 (vige-wechat): Mint UI 2.x
- **路由**: Vue Router 3.x
- **状态管理**: Vuex 3.x
- **HTTP 客户端**: Axios
- **构建工具**: Vue CLI 3.x

---

## 项目结构

### Monorepo 结构
```
vige/
├── vige-api/              # FastAPI 后端
├── vige-web/              # Web 前台客户端
├── vige-bo/               # 管理后台客户端
├── vige-wechat/           # 微信 H5 客户端
├── docker-compose.yml     # Docker 编排文件
└── Makefile               # 项目构建脚本
```

### 后端 (vige-api) 结构
```
vige-api/
├── vige/
│   ├── api/               # API 模块
│   │   ├── bo_user/       # 后台用户模块
│   │   ├── users/         # 前台用户模块
│   │   ├── media/         # 媒体文件模块
│   │   ├── settings/      # 配置模块
│   │   ├── wechat/        # 微信集成模块
│   │   ├── notifications/ # 通知模块
│   │   ├── __init__.py    # API 路由注册
│   │   ├── jwt.py         # JWT 认证
│   │   ├── decorators.py  # 装饰器
│   │   └── utils.py       # 工具函数
│   ├── migrations/        # Alembic 数据库迁移
│   ├── tests/             # 测试
│   ├── translations/      # 国际化翻译文件
│   ├── app_factory.py     # 应用工厂
│   ├── app.py             # 应用入口
│   ├── config.py          # 配置管理
│   ├── db.py              # 数据库连接
│   ├── huey_app.py        # Huey 异步任务
│   ├── log.py             # 日志配置
│   └── cli.py             # CLI 命令
├── Pipfile                # Pipenv 依赖
├── Dockerfile             # Docker 构建文件
├── entrypoint.sh          # 容器入口脚本
└── Makefile               # 构建脚本
```

### 前端 (vige-bo/vige-web/vige-wechat) 通用结构
```
vige-*/
├── config/                # 环境配置
├── public/                # 静态资源
├── src/
│   ├── assets/            # 资源文件
│   ├── components/        # 通用组件
│   ├── config/            # 配置
│   ├── libs/              # 工具库
│   ├── locale/            # 国际化
│   ├── router/            # 路由
│   ├── store/             # Vuex 状态管理
│   ├── styles/            # 样式
│   ├── view/              # 页面视图
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── package.json
└── vue.config.js
```

---

## 核心模块详解

### 1. 应用初始化 ([app_factory.py](file:///workspace/vige-api/vige/app_factory.py))

#### 核心功能
- FastAPI 应用实例创建
- Redis 客户端初始化
- 静态文件挂载 (`/media`)
- 请求上下文管理
- 中间件配置
- 全局异常处理

#### 关键组件

**Redis 客户端**
```python
redis_client = redis.Redis(
    host=config.REDIS_HOST or 'localhost',
    port=config.REDIS_PORT or 6379,
    db=config.REDIS_DB or 0,
)
```

**请求中间件**
- 标记请求是否来自后台 (`from_bo`)
- 请求上下文变量管理

**健康检查端点**
- `/v1/ping`: 简单健康检查

### 2. 配置管理 ([config.py](file:///workspace/vige-api/vige/config.py))

#### 配置类 `Settings`
基于 Pydantic Settings，支持从环境变量和 `local_config.env` 文件加载配置。

**核心配置项**:
```python
class Settings(BaseSettings):
    # 基础配置
    ENV: str = 'local'
    DEBUG: bool = True
    SECRET_KEY: str = 'secret_key'
    
    # 数据库
    SQLALCHEMY_DATABASE_URI: str = 'postgresql://@/vige'
    
    # JWT 认证
    AUTHJWT_SECRET_KEY: str = 'jwt_secret_key'
    AUTHJWT_ACCESS_TOKEN_EXPIRES: int = 3600 * 24 * 7  # 7天
    
    # Redis
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 10
    
    # 文件上传
    UPLOADS_DEFAULT_DEST: str = './instance'
    DEFAULT_THUMBNAIL_SIZE: Tuple[int, int] = (400, 400)
    
    # 微信
    WECHAT_APP_ID: str = ''
    WECHAT_APP_SECRET: str = ''
    
    # 其他第三方服务配置...
```

### 3. 数据库管理 ([db.py](file:///workspace/vige-api/vige/db.py))

#### 核心类

**DatabaseSessionManager**
- 数据库会话管理
- 事务范围管理 (`transaction_scope`)
- 依赖注入 (`get_db`)

**CRUDMixin**
基础 CRUD 操作 mixin，提供：
- `create()`: 创建对象
- `get()` / `get_or_404()`: 获取对象
- `exists()`: 检查存在性
- `paginated_dump()`: 分页查询与序列化
- `save()` / `update()` / `delete()`: 持久化操作

**ProfileMixin**
- JSONB profile 字段支持
- 属性装饰器：`json_property`、`string_property`、`datetime_property`、`integer_property`、`float_property`、`bool_property`、`object_property`、`array_property`、`price_property`、`date_property`

**TrackableMixin**
- `created_at` / `updated_at` 时间戳
- `created_by` / `updated_by` 审计字段

**SoftDeleteMixin**
- 软删除支持
- `deleted_at` 字段
- `QueryWithSoftDelete` 查询类

### 4. 后台用户模块 ([bo_user](file:///workspace/vige-api/vige/api/bo_user/))

#### 核心功能
- 后台用户登录（支持简单登录和 2FA 双因素认证）
- 用户管理（CRUD）
- 角色管理
- 权限控制

#### API 端点

**认证相关**
- `POST /v1/admin/login`: 后台登录
- `POST /v1/admin/logout`: 登出
- `POST /v1/admin/2fa/verify`: 2FA 验证码验证
- `GET /v1/admin/users/me`: 获取当前用户信息

**用户管理**
- `GET /v1/admin/users`: 用户列表（分页）
- `GET /v1/admin/users/options`: 用户选项列表
- `GET /v1/admin/users/{id}`: 获取单个用户
- `POST /v1/admin/users`: 创建用户
- `PUT /v1/admin/users/{id}`: 更新用户
- `PUT /v1/admin/users/update_password`: 更新密码
- `POST /v1/admin/users/{id}/{mode}`: 启用/禁用用户
- `POST /v1/admin/users/upload`: 批量导入用户

**角色管理**
- `GET /v1/admin/roles`: 角色列表
- `GET /v1/admin/roles/options`: 角色选项
- `GET /v1/admin/roles/{id}`: 获取单个角色
- `POST /v1/admin/roles`: 创建角色
- `PUT /v1/admin/roles/{id}`: 更新角色
- `POST /v1/admin/roles/{id}/{mode}`: 启用/禁用角色
- `GET /v1/admin/permissions`: 权限列表

#### 数据模型

**BoRole** - 后台角色
```python
class BoRole(CRUDMixin):
    name: str (唯一)
    description: str
    permissions: List[BoRoleXPermission]
    disabled_at: datetime
```

**BoUser** - 后台用户
```python
class BoUser(CRUDMixin, ProfileMixin):
    nickname: str
    username: str (唯一)
    password: str (哈希)
    mobile: str
    active: bool
    role_id: int (外键)
    role: BoRole (关系)
    @property permissions: List[str]
```

**BoRoleXPermission** - 角色权限关联
```python
class BoRoleXPermission(CRUDMixin):
    role_id: int
    permission: str
```

#### 权限装饰器
- `@bo_required`: 后台用户认证
- `@perm_accepted(permissions)`: 权限检查

### 5. 前台用户模块 ([users](file:///workspace/vige-api/vige/api/users/))

#### 核心功能
- 用户登录（短信验证码）
- 用户信息管理

#### API 端点
- `GET /v1/web/users/me`: 获取当前用户
- `POST /v1/web/send_code`: 发送登录验证码
- `POST /v1/web/login`: 用户登录
- `POST /v1/web/logout`: 登出

#### 数据模型

**User** - 前台用户
```python
class User(CRUDMixin, ProfileMixin):
    openid: str (唯一，微信 openid)
    mobile: str (唯一)
    nickname: str
    avatar_id: int (外键到 MediaModel)
    avatar: MediaModel (关系)
    created_at: datetime
    updated_at: datetime
    disabled_at: datetime
    @string_property source: str
```

### 6. 媒体文件模块 ([media](file:///workspace/vige-api/vige/api/media/))

#### 核心功能
- 图片上传
- 缩略图自动生成
- 文件 URL 管理

#### API 端点
- `POST /v1/media`: 上传图片

#### 数据模型

**MediaModel** - 媒体文件
```python
class MediaModel(CRUDMixin, ProfileMixin):
    object_type: str (泛型关联类型)
    object_id: int (泛型关联 ID)
    @string_property filename: str
    @property url: str
    @property thumbnail_url: str
```

#### 支持的图片格式
- 常见图片格式 (jpg, png, gif 等)
- 自动生成 400x400 缩略图

### 7. 微信集成模块 ([wechat](file:///workspace/vige-api/vige/api/wechat/))

#### 核心功能
- 微信二维码生成
- 微信用户绑定
- 微信 JS-SDK 配置
- 微信事件处理

#### API 端点
- `GET /v1/wechat/orange/qr_code`: 获取绑定二维码
- `POST /v1/wechat/orange/bind_user`: 绑定用户
- `GET /v1/wechat/wx_configs`: 获取 JS-SDK 配置
- `GET /v1/wechat/events`: 微信服务验证
- `POST /v1/wechat/events`: 微信事件推送处理

### 8. 配置管理模块 ([settings](file:///workspace/vige-api/vige/api/settings/))

#### 核心功能
- 动态配置管理
- 配置实时生效

#### API 端点
- `GET /v1/admin/configs`: 获取配置列表
- `PUT /v1/admin/configs`: 更新配置

### 9. JWT 认证模块 ([jwt.py](file:///workspace/vige-api/vige/api/jwt.py))

#### 认证流程
1. 用户登录时创建 JWT token
2. Token 存储在 Cookie 和请求头中
3. 后续请求通过 `@bo_required` 或 `@user_required` 装饰器验证
4. 支持 CSRF 保护

---

## 数据库模型

### ER 图概要
```
BoUser ──┬──> BoRole
         │
         └──> BoRoleXPermission ──> BoPermission

User ──> MediaModel (avatar)

MediaModel (泛型关联) ──> 任意对象
```

### 迁移管理
使用 Alembic 进行数据库迁移，迁移文件位于 `vige-api/vige/migrations/versions/`。

**常用命令** (在 vige-api 目录下):
```bash
# 生成迁移
make db "描述信息"

# 应用迁移
make upgrade-db

# 查看当前版本
make config-db
```

---

## API 接口规范

### 基础路径
所有 API 端点前缀为 `/v1`

### 认证方式
- **JWT Token**: 存储在 Cookie (`vige_auth_cookie`) 或 Authorization Header
- **CSRF 保护**: CSRF Token 存储在 Cookie (`vige_auth_csrf_cookie`)，需在请求头中携带

### 统一响应格式

**成功响应**
```json
{
  "success": true,
  "data": {...}
}
```

**失败响应**
```json
{
  "success": false,
  "message": "错误信息",
  "details": {...}  // 可选
}
```

### 分页响应
```json
{
  "success": true,
  "rows": [...],
  "pagination": {
    "page": 1,
    "total": 100,
    "has_prev": false,
    "has_next": true,
    "first": 1
  }
}
```

---

## 前端架构

### 管理后台 (vige-bo)

#### 技术栈
- Vue 2 + iView 3.x
- Vue Router + Vuex
- Axios 统一拦截

#### 核心页面
- 登录页
- 首页 / 仪表板
- 用户管理
- 角色管理
- 系统配置

#### 目录说明
- `src/components/Tinymce/`: 富文本编辑器组件
- `src/components/charts/`: 图表组件
- `src/components/common/`: 通用组件
- `src/components/media/`: 媒体组件
- `src/components/tables/`: 表格组件
- `src/view/system/`: 系统管理页面
- `src/view/users/`: 用户管理页面

### 前台 Web (vige-web)

#### 技术栈
- Vue 2 + iView 3.x
- 支持 Markdown 渲染

### 微信 H5 (vige-wechat)

#### 技术栈
- Vue 2 + Mint UI
- 微信 SDK 集成

---

## 配置与部署

### 环境要求
- Python 3.10
- PostgreSQL 14+
- Redis 6+
- Node.js 14+ (前端开发)
- Yarn (前端包管理)

### 本地配置文件

**后端配置**: `vige-api/vige/local_config.env`
```env
ENV=local
DEBUG=true
SECRET_KEY=your-secret-key
AUTHJWT_SECRET_KEY=your-jwt-secret
SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@localhost:5432/vige
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=10
EXTERNAL_URL=http://localhost:8000
UPLOADS_DEFAULT_DEST=./instance
```

### Docker 部署

**使用 docker-compose 启动**
```bash
docker-compose up -d
```

服务:
- `postgres`: PostgreSQL 数据库 (端口 5432)
- `redis`: Redis (端口 6379)
- `api`: FastAPI 后端 (端口 8000)

**后端 Docker 镜像**
```bash
cd vige-api
docker build -t vige-api .

# 运行 web 服务
docker run -p 8000:8000 -v $(pwd)/vige/local_config.env:/vige/vige/local_config.env vige-api web

# 运行 worker
docker run -v $(pwd)/vige/local_config.env:/vige/vige/local_config.env vige-api worker
```

### 后端开发启动

```bash
cd vige-api

# 安装依赖
make install

# 进入虚拟环境
pipenv shell

# 创建数据库
createdb vige

# 执行迁移
make upgrade-db

# 初始化管理员（可选）
make create-role
make create-user
make set-role
make set-perm

# 启动开发服务器
make run

# 启动异步任务 worker（另一个终端）
make worker
```

访问:
- API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 前端开发启动

**管理后台 (vige-bo)**
```bash
cd vige-bo
yarn install
yarn dev
```

**前台 (vige-web)**
```bash
cd vige-web
yarn install
yarn dev
```

**微信 H5 (vige-wechat)**
```bash
cd vige-wechat
yarn install
yarn dev
```

---

## 开发指南

### 后端开发

#### 添加新的 API 模块
1. 在 `vige/api/` 下创建新目录
2. 创建 `models.py` 定义数据模型
3. 创建 `forms.py` 定义请求验证表单
4. 创建 `api.py` 定义路由和处理函数
5. 在 `vige/api/__init__.py` 的 `install()` 函数中注册模块

#### 数据库模型开发规范
- 继承 `CRUDMixin`（必需）
- 根据需要继承 `ProfileMixin`、`TrackableMixin`、`SoftDeleteMixin`
- 使用 `Mapped` 和 `mapped_column` 定义字段
- 实现 `dump()` 方法进行序列化

#### 权限系统
权限定义在 `vige/api/constants.py` 中的 `BoPermission` 枚举。

使用 `@perm_accepted(permission1, permission2, ...)` 装饰器保护端点。

### 前端开发

#### API 调用
统一使用 `src/libs/api.js` 中封装的 API 方法。

#### 状态管理
使用 Vuex，模块位于 `src/store/module/`。

#### 路由配置
路由定义在 `src/router/routers.js`。

### 代码规范
- 后端: 使用 pre-commit hooks (ruff, black, isort)
- 前端: 使用 ESLint

### 测试
```bash
# 后端测试
cd vige-api
make test

# 前端测试
cd vige-*
yarn test:unit
yarn test:e2e
```

---

## 常见问题

### 数据库迁移问题
- 迁移失败时检查 `alembic_version` 表
- 可以使用 `pipenv run alembic downgrade -1` 回滚

### Redis 连接问题
- 确保 Redis 服务已启动
- 检查 `local_config.env` 中的 Redis 配置

### 媒体文件访问
- 文件存储在 `UPLOADS_DEFAULT_DEST` (默认为 `./instance`)
- 通过 `/media/{filename}` 访问
- 缩略图文件名为 `{filename}_thumbnail.{ext}`

---

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

MIT License

---

*最后更新: 2026-06-08*
