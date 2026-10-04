# 计算器后端（Calculator Backend）

一个「前后端分离计算器系统」的后端部分，负责表达式计算、输入校验、异常处理，以及计算历史的存储与管理。

## 项目介绍

- 前端（安卓 App）通过 HTTP API 调用本后端完成计算，前端只负责界面与交互，**核心计算全部由后端完成**。
- 后端职责：表达式解析与计算、输入校验、异常处理、历史记录的增/查/删。
- 表达式计算由**手写的递归下降解析器**完成，**未使用 `eval` / `exec` 等任意代码执行方式**。

## 技术栈

| 项 | 技术 |
|---|---|
| 语言 | Python 3.13 |
| Web 框架 | Flask 3.1 |
| 数据库 | SQLite（Python 内置 `sqlite3`，无需额外安装） |

## 运行环境

- Python 3.9 及以上（开发使用 3.13）
- 依赖见 `requirements.txt`（仅 Flask）

## 安装方法

```bash
# 1. 在项目目录创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境（Windows）
.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

## 启动方法

```bash
python app.py
```

启动后服务监听 `http://127.0.0.1:5000`，可用浏览器访问 `/api/health` 验证。

## 配置说明

- 默认端口为 `5000`，生产环境通过 `PORT` 环境变量传入。
- 数据库文件 `calculator.db` 会在首次启动时自动生成于项目目录下；部署到有持久化磁盘的平台时，可用 `CALCULATOR_DB_FILE` 指定数据库路径。

## 数据库初始化方法

**无需手动初始化。** 首次启动 `app.py` 时会自动执行 `init_db()` 建表。

表结构 `calculation_history`：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 主键，自增 |
| expression | TEXT | 计算表达式 |
| result | TEXT | 计算结果 |
| created_at | TEXT | 计算时间（`YYYY-MM-DD HH:MM:SS`） |

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/calculate` | 计算表达式（成功自动存历史） |
| GET | `/api/history` | 查询所有历史 |
| DELETE | `/api/history/<id>` | 删除指定 id 的历史 |
| DELETE | `/api/history` | 清空全部历史 |
| GET | `/api/health` | 健康检查 |

## 前后端连接方式

前端通过 HTTP + JSON 调用上述接口。示例：

计算请求：

```json
POST /api/calculate
{ "expression": "1+2*3" }
```

成功响应：

```json
{ "success": true, "expression": "1+2*3", "result": 7 }
```

失败响应：

```json
{ "success": false, "message": "不能除以 0" }
```

## 自动化测试

```bash
python -m unittest discover -v
```

测试覆盖解析器优先级、括号、小数、一元符号、非法输入、除零，以及 Flask API 的持久化、查询和删除。

## 部署

项目包含 `Dockerfile` 和 `render.yaml`，可部署到支持 Docker 的 Web 服务。服务会读取 `PORT` 环境变量，健康检查路径为 `/api/health`。生产环境建议使用 HTTPS，并为 SQLite 文件配置持久化磁盘或迁移到托管数据库。

### 使用 Render 部署

1. 将 `calculator_backend` 单独推送到 GitHub 仓库。
2. 在 Render 中选择 **New > Web Service**，连接该仓库。
3. 选择 Docker 运行方式，Dockerfile 使用仓库根目录的 `Dockerfile`。
4. 健康检查路径填写 `/api/health`，创建服务并等待构建完成。
5. 浏览器访问 `https://你的服务名.onrender.com/api/health`，看到 `{"status":"ok"}` 后说明部署成功。
6. 把这个 HTTPS 地址写入 Android 的 `MainActivity.java` 中 `BACKEND_URLS` 的第一项，然后重新构建 APK。

Render 免费实例可能会休眠，首次访问需要等待启动；SQLite 在没有持久化磁盘时也可能随实例重建而清空。演示需要稳定保存历史时，应为服务配置持久化磁盘，或改用托管数据库。

## 目录结构

```
calculator_backend/
├── app.py            # 入口与路由（控制器层）
├── calculator.py     # 表达式解析与计算（业务层）
├── database.py       # 数据库操作（数据层）
├── requirements.txt  # 依赖清单
├── README.md         # 本文件
└── codestyle.md      # 代码规范
```
