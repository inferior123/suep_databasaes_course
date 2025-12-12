# 作业管理系统 / Assignment Management System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-%234FC08D?logo=vuedotjs)](https://vuejs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange?logo=mysql)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

> 一个面向高校教学场景的全生命周期作业管理平台，支持教师发布作业、学生提交作业、成绩评定与过程性评价，助力教育数字化转型。

> A full-lifecycle assignment management platform designed for higher education, enabling teachers to assign tasks, students to submit work, and facilitating grading and formative assessment—supporting the digital transformation of education.

## 🌟 功能亮点 / Key Features

- **统一任务中心**：学生清晰查看所有课程作业及截止时间  
  *Unified task center: Students can clearly view all assignments and deadlines across courses.*

- **角色化工作台**：教师端支持作业发布、批改、成绩录入；学生端支持选课与作业提交  
  *Role-based dashboards: Teachers can publish, grade, and record scores; students can enroll in courses and submit assignments.*

- **过程性评价支持**：完整记录每次作业提交与成绩，构建学习行为画像  
  *Supports formative assessment by tracking submission history and performance over time.*

- **安全认证体系**：基于 JWT 的身份验证与细粒度权限控制（RBAC）  
  *Secure authentication with JWT and fine-grained role-based access control (RBAC).*

- **现代化技术栈**：前后端分离架构，高性能、高可维护性  
  *Modern tech stack: Fully decoupled frontend and backend for high performance and maintainability.*

## 🛠 技术栈 / Tech Stack

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + Composition API, Pinia, Vue Router, Vite, Tailwind CSS |
| **后端** | FastAPI (Python), Pydantic, SQLAlchemy, JWT |
| **数据库** | MySQL 8.0+ (InnoDB) |
| **工具** | Git, Alembic (数据库迁移), Postman (API 测试) |

## 🚀 快速启动 / Quick Start

### 前置要求 / Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### 后端设置 / Backend Setup
```bash
# 克隆项目
git clone https://github.com/your-username/assignment-management-system.git
cd assignment-management-system/backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate （Windows）

# 安装依赖
pip install -r requirements.txt

# 配置数据库（修改 .env 或 config.py 中的数据库连接信息）
# 初始化数据库（使用 Alembic）
alembic upgrade head

# 启动服务
uvicorn main:app --reload --port 8000
```

### 前端设置 / Frontend Setup
```bash
cd ../frontend

# 安装依赖
npm install

# 启动开发服务器（默认代理到 http://localhost:8000）
npm run dev
```

访问 [http://localhost:5173](http://localhost:5173) 即可开始使用。

## 📁 项目结构 / Project Structure

```
assignment-management-system/
├── backend/               # FastAPI 后端服务
│   ├── main.py            # 应用入口
│   ├── models/            # 数据库模型
│   ├── schemas/           # Pydantic 数据校验模型
│   ├── api/               # 路由与业务逻辑
│   └── core/              # 安全、配置等核心模块
├── frontend/              # Vue 3 前端应用
│   ├── src/
│   │   ├── views/         # 页面组件（登录、教师主页、学生主页等）
│   │   ├── stores/        # Pinia 状态管理
│   │   └── router/        # 路由配置
└── docs/                  # 设计文档、ER 图、接口说明等
```

## 📝 开发团队 / Development Team

本项目由上海电力学院 2022 级信息与计算科学专业团队开发完成：
- [@stevengeyue](https://github.com/stevengeyue) 数据库设计与实现、数据抽象层开发
- [@inferior123](https://github.com/inferior123)：登录模块、教师工作台（全栈）

## 📄 许可证 / License

本项目采用 [MIT License](LICENSE) 开源协议。
