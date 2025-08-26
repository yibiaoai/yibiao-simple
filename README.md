# AI写标书助手

一个基于 FastAPI + React 的现代化智能标书写作助手，可以自动解析招标文件并生成标书内容。

## 功能特性

- 📄 支持Word (.docx) 和PDF (.pdf) 格式的招标文件上传
- 🤖 使用OpenAI API智能解析招标文件
- 📋 自动提取项目概述和技术评分要求
- 📝 智能生成标书目录结构和章节内容
- ⚙️ 支持自定义API配置（API Key和Base URL）
- 💾 本地配置文件持久化存储
- 🎨 现代化的React + Tailwind CSS界面
- 🚀 基于FastAPI的高性能后端API

## 项目架构

```
yibiao-simple/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── main.py         # FastAPI应用入口
│   │   ├── config.py       # 配置管理
│   │   ├── models/         # 数据模型
│   │   ├── routers/        # API路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── requirements.txt    # 后端依赖
│   └── run.py             # 后端启动脚本
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # 可复用组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API调用
│   │   ├── hooks/          # 自定义Hooks
│   │   └── types/          # 类型定义
│   ├── package.json
│   └── tailwind.config.js
├── app.py                  # 主启动脚本
├── build.py               # 构建脚本
├── run.bat                # Windows启动脚本
└── build.bat              # Windows构建脚本
```

## 安装和运行

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 开发环境运行

#### 方式一：使用启动脚本（推荐）

Windows:
```bash
run.bat
```

或直接运行:
```bash
python app.py
```

#### 方式二：分别启动前后端

1. 启动后端：
```bash
cd backend
pip install -r requirements.txt
python run.py
```

2. 启动前端：
```bash
cd frontend
npm install
npm start
```

### 打包成exe文件

#### Windows一键打包
```bash
build.bat
```

或手动执行：
```bash
python build.py
```

构建完成后，exe文件位于 `dist/AI写标书助手.exe`

## 使用说明

### 三步完成标书编写

1. **标书解析**
   - 在左侧配置面板输入OpenAI API Key
   - 上传招标文件（Word或PDF格式）
   - 点击分析按钮，AI自动提取项目概述和技术评分要求

2. **目录编辑**  
   - 基于分析结果生成专业的标书目录结构
   - 支持三级目录层次
   - 可为每个章节生成具体内容

3. **正文编辑**
   - 查看和编辑各章节的具体内容
   - 支持内容修改和重新生成
   - 实时统计字数和完成进度

## 技术栈

### 后端
- **框架**：FastAPI 0.104+
- **异步支持**：uvicorn, asyncio
- **AI服务**：OpenAI API
- **文档处理**：python-docx, PyPDF2
- **数据验证**：Pydantic

### 前端  
- **框架**：React 18 + TypeScript
- **样式**：Tailwind CSS
- **图标**：Heroicons
- **HTTP客户端**：Axios
- **状态管理**：React Hooks

### 打包工具
- **Python打包**：PyInstaller
- **前端构建**：Create React App

## API文档

启动后访问 `http://localhost:8000/docs` 查看完整的API文档。

## 配置说明

### OpenAI API配置
- **API Key**: 必填，用于调用OpenAI API
- **Base URL**: 可选，支持使用代理或其他兼容服务
- **模型**: 支持GPT-3.5-turbo、GPT-4等模型

### 支持的文件格式
- Word文档：`.docx`
- PDF文档：`.pdf`  
- 最大文件大小：10MB

## 注意事项

- 需要稳定的网络连接访问OpenAI API
- 建议使用Chrome、Edge或Firefox浏览器
- 首次运行需要安装依赖，可能需要几分钟时间
- 配置信息会保存在用户目录的 `.ai_write_helper` 文件夹中

## 开发指南

详细的开发指南请查看 `CLAUDE.md` 文件。