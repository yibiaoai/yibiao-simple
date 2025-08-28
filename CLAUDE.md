# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 FastAPI + React 的现代化 AI 写标书助手应用，使用 OpenAI API 智能解析招标文件并生成标书内容。项目采用前后端分离架构，提供现代化的Web界面和高性能API服务。

## 常用命令

### 开发环境启动
```bash
# 一键启动（推荐）
python app.py

# 或使用批处理脚本（Windows）
run.bat

# 分别启动后端
cd backend
pip install -r requirements.txt  
python run.py

# 分别启动前端
cd frontend
npm install
npm start
```

### 构建和打包
```bash
# 一键构建exe
python build.py

# 或使用批处理脚本（Windows）
build.bat
```

## 项目架构

### 整体架构
项目采用前后端分离的架构模式：
- **后端**: FastAPI + uvicorn，提供RESTful API和异步处理
- **前端**: React + TypeScript + Tailwind CSS，现代化SPA应用
- **打包**: PyInstaller + 静态文件集成，生成单个exe文件

### 后端架构 (FastAPI)
```
backend/
├── app/
│   ├── main.py              # FastAPI应用入口，路由注册
│   ├── config.py            # 应用配置和设置
│   ├── models/
│   │   └── schemas.py       # Pydantic数据模型定义
│   ├── routers/             # API路由模块
│   │   ├── config.py        # 配置管理API
│   │   ├── document.py      # 文档处理API
│   │   └── outline.py       # 目录管理API
│   ├── services/            # 业务逻辑服务
│   │   ├── openai_service.py    # OpenAI API封装
│   │   └── file_service.py      # 文件处理服务
│   └── utils/
│       └── config_manager.py    # 配置管理工具
├── requirements.txt         # Python依赖
└── run.py                  # 后端启动脚本
```

### 前端架构 (React)
```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── ConfigPanel.tsx  # 配置面板组件
│   │   └── StepBar.tsx      # 步骤导航组件
│   ├── pages/               # 页面组件
│   │   ├── DocumentAnalysis.tsx  # 文档分析页面
│   │   ├── OutlineEdit.tsx       # 目录编辑页面
│   │   └── ContentEdit.tsx       # 内容编辑页面
│   ├── services/
│   │   └── api.ts           # API调用封装
│   ├── hooks/
│   │   └── useAppState.ts   # 应用状态管理Hook
│   ├── types/
│   │   └── index.ts         # TypeScript类型定义
│   └── App.tsx             # 主应用组件
├── package.json
├── tailwind.config.js       # Tailwind CSS配置
└── .env                    # 环境变量
```

### 核心功能模块

#### 1. 配置管理 (backend/app/routers/config.py)
- 配置保存和加载：`POST /api/config/save`, `GET /api/config/load`
- 模型列表获取：`POST /api/config/models`
- 本地配置文件管理（存储在用户目录 `.ai_write_helper/`）

#### 2. 文档处理 (backend/app/routers/document.py) 
- 文件上传：`POST /api/document/upload`
- 文档分析：`POST /api/document/analyze` (普通) / `POST /api/document/analyze-stream` (流式)
- 支持Word (.docx)和PDF (.pdf)格式

#### 3. 目录管理 (backend/app/routers/outline.py)
- 目录生成：`POST /api/outline/generate` (普通) / `POST /api/outline/generate-stream` (流式)
- 内容生成：`POST /api/outline/generate-content` (普通) / `POST /api/outline/generate-content-stream` (流式)

#### 4. OpenAI服务 (backend/app/services/openai_service.py)
核心AI功能封装：
- `analyze_document()`: 文档分析，提取项目概述和技术评分要求
- `generate_outline()`: 基于分析结果生成三级目录结构
- `generate_content_for_outline()`: 为叶子节点生成具体内容
- 支持异步和流式响应

#### 5. 前端状态管理 (frontend/src/hooks/useAppState.ts)
使用React Hooks管理应用状态：
- 当前步骤导航状态
- API配置信息
- 文档内容和分析结果
- 目录结构数据
- 选中章节信息

### 页面流程
1. **标书解析页面** - 上传文档，使用AI提取项目概述和技术评分要求
2. **目录编辑页面** - 基于解析结果生成专业标书目录结构，支持内容生成
3. **正文编辑页面** - 查看和编辑各章节具体内容，支持统计和修改

### API设计特点
- RESTful API设计
- 支持流式响应（Server-Sent Events）
- 统一的错误处理和响应格式
- Pydantic数据验证
- CORS跨域支持
- 自动API文档生成 (访问 `/docs`)

### 技术栈细节

#### 后端技术栈
- **FastAPI 0.104+**: 现代Python Web框架
- **uvicorn**: ASGI服务器，支持异步处理
- **Pydantic**: 数据验证和序列化
- **python-docx**: Word文档处理
- **PyPDF2**: PDF文档处理  
- **OpenAI**: AI服务调用
- **aiofiles**: 异步文件操作

#### 前端技术栈
- **React 18**: 现代前端框架
- **TypeScript**: 类型安全的JavaScript
- **Tailwind CSS**: 原子化CSS框架
- **Heroicons**: 图标库
- **Axios**: HTTP客户端

### 部署和打包
- 开发模式：前后端分离运行，支持热重载
- 生产模式：前端构建为静态文件，集成到FastAPI服务
- exe打包：使用PyInstaller打包Python应用，包含前端静态文件

## 开发注意事项

- 所有UI文本使用简体中文
- API接口需要提供中文错误信息
- 使用Windows命令行格式的脚本命令
- 前后端接口需要保持类型一致性（TypeScript接口与Pydantic模型）
- 异步操作需要适当的错误处理和用户反馈
- 文件上传需要考虑大小限制和安全性
- 流式响应需要处理网络中断和重连
- 每次安装依赖都要检查并修改 build.py 和  /backend/requirements.txt