# 易标极速版 - AI智能标书写作助手

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/React-18+-61dafb.svg" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

<p align="left">
  <strong>🚀 基于 AI 的智能标书写作助手，让标书制作变得简单高效</strong>
</p>



### ✨ 核心功能

- **🤖 智能文档解析**：自动分析招标文件，提取关键信息和技术评分要求
- **📝 AI生成目录**：基于招标文件智能生成专业的三级标书目录结构  
- **⚡ 内容自动生成**：为每个章节自动生成高质量、针对性的标书内容
- **🎯 个性化定制**：支持***自定义AI模型***
- **💾 一键导出**：导出word，自由编辑

### 🌟 产品优势

- ⏱️ **效率提升**: 将传统需要数天的标书制作缩短至几小时
- 🎨 **专业质量**: AI生成的内容结构清晰、逻辑严密、符合行业标准
- 🔧 **易于使用**: 简洁直观的界面设计，无需专业培训即可上手
- 🔄 **持续优化**: 基于用户反馈不断改进AI算法和用户体验

## 🌐 官方网站

**访问官网**: [https://yibiao.pro](https://yibiao.pro)

获取更多产品信息、在线体验和技术支持。

## 📦 使用说明

### 💻 系统要求

- Windows 10/11 (64位)
- 至少 4GB 内存
- 100MB 可用磁盘空间

### ⬇️ 下载安装

1. **直接下载**：从 [GitHub Releases](https://github.com/your-username/易标极速版/releases) 下载最新版本的exe文件
2. **运行程序**：双击 `易标极速版.exe` 即可启动应用
3. **配置AI**：首次使用需要配置OpenAI API密钥（支持国内代理）

### 🚀 快速开始

#### 方式一：下载使用（推荐）

```
1. 下载最新版本exe文件
2. 双击运行易标极速版.exe
3. 配置AI模型和API密钥
4. 上传招标文件开始使用
```

#### 方式二：开发环境运行

```bash
# 克隆项目
git clone https://github.com/your-username/易标极速版.git
cd 易标极速版

# 一键启动
python app.py

# 或使用Windows批处理
run.bat

# 或分别启动
# 后端
cd backend
pip install -r requirements.txt
python run.py

# 前端 (新终端)
cd frontend
npm install
npm start
```

### 📝 使用流程

1. **📄 上传文档**：上传招标文件（支持Word和PDF格式）
2. **🔍 智能分析**：AI自动解析文档，提取项目概述和技术要求
3. **📋 生成目录**：基于分析结果智能生成标书目录结构
4. **✍️ 内容编辑**：为各章节生成内容并进行个性化编辑
5. **📤 导出标书**：一键导出完整的标书文档

## 🛠️ 技术架构

### 架构设计

采用现代化的**前后端分离架构**，确保高性能和良好的用户体验：

- **前端**: React + TypeScript + Tailwind CSS
- **后端**: FastAPI + Python
- **AI集成**: OpenAI API
- **部署**: PyInstaller 单文件打包

### 🔧 技术栈

#### 后端技术

| 技术        | 版本   | 说明             |
| ----------- | ------ | ---------------- |
| Python      | 3.8+   | 核心编程语言     |
| FastAPI     | 0.104+ | 高性能Web框架    |
| Uvicorn     | -      | ASGI服务器       |
| Pydantic    | -      | 数据验证和序列化 |
| OpenAI      | -      | AI服务集成       |
| python-docx | -      | Word文档处理     |
| PyPDF2      | -      | PDF文档处理      |

#### 前端技术

| 技术         | 版本 | 说明                 |
| ------------ | ---- | -------------------- |
| React        | 18+  | 现代前端框架         |
| TypeScript   | -    | 类型安全的JavaScript |
| Tailwind CSS | -    | 原子化CSS框架        |
| Axios        | -    | HTTP客户端           |
| Heroicons    | -    | 图标库               |

### 🏗️ 项目结构

```
易标极速版/
├── 📁 backend/                 # 后端服务
│   ├── 📁 app/
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── config.py          # 应用配置
│   │   ├── 📁 routers/        # API路由模块
│   │   ├── 📁 services/       # 业务逻辑服务  
│   │   └── 📁 models/         # 数据模型
│   └── requirements.txt       # Python依赖
├── 📁 frontend/               # 前端应用
│   ├── 📁 src/
│   │   ├── 📁 components/     # 可复用组件
│   │   ├── 📁 pages/          # 页面组件
│   │   ├── 📁 services/       # API服务
│   │   └── 📁 hooks/          # React Hooks
│   └── package.json           # 前端依赖
├── 📁 screenshots/            # 应用截图
├── app.py                     # 一键启动脚本
├── build.py                   # 打包脚本
└── README.md                  # 项目文档
```

### 🔄 核心功能模块

- **配置管理模块**: 支持多种AI模型配置和本地设置保存
- **文档处理模块**: 智能解析Word和PDF格式的招标文件
- **AI服务模块**: 集成OpenAI API，提供文档分析和内容生成
- **目录生成模块**: 基于AI分析结果生成专业标书目录
- **内容编辑模块**: 提供富文本编辑和实时预览功能

## 📸 应用截图

### 主界面预览

![主界面](./screenshots/main-interface.png)

### 文档分析页面  

![文档分析](./screenshots/document-analysis.png)

### 目录编辑界面

![目录编辑](./screenshots/outline-edit.png)

### 内容生成页面

![内容生成](./screenshots/content-generation.png)

## 🎯 配置说明

### OpenAI API配置

- **API Key**: 必填，用于调用OpenAI API
- **Base URL**: 可选，支持使用代理或其他兼容服务
- **模型**: 支持GPT-3.5-turbo、GPT-4等模型

### 支持的文件格式

- Word文档：`.docx` (推荐)
- PDF文档：`.pdf`  
- 最大文件大小：10MB

## 🚀 部署和打包

### 开发环境

```bash
# 一键启动开发环境
python app.py

# Windows批处理脚本
run.bat
```

### 生产环境打包

```bash
# 一键构建exe
python build.py

# Windows批处理脚本
build.bat
```

构建完成后，exe文件位于 `dist/易标极速版.exe`

## 📚 API文档

启动应用后访问 `http://localhost:8000/docs` 查看完整的FastAPI自动生成的API文档。

## 🤝 贡献指南

欢迎各种形式的贡献！

1. **🐛 问题反馈**: 在 [Issues](https://github.com/your-username/易标极速版/issues) 中报告bug
2. **💡 功能建议**: 提出新功能需求和改进建议  
3. **🔧 代码贡献**: Fork项目，提交Pull Request
4. **📖 文档完善**: 帮助改进文档和使用说明

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/易标极速版.git
cd 易标极速版

# 安装依赖
pip install -r backend/requirements.txt
cd frontend && npm install
```

## ⚠️ 注意事项

- 需要稳定的网络连接访问OpenAI API
- 建议使用Chrome、Edge或Firefox浏览器
- 首次运行需要安装依赖，可能需要几分钟时间
- 配置信息会保存在用户目录的 `.ai_write_helper` 文件夹中
- 使用前请确保已正确配置OpenAI API Key

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源协议发布。

## 🙋‍♂️ 联系我们

- **官方网站**: [https://yibiao.pro](https://yibiao.pro)
- **问题反馈**: [GitHub Issues](https://github.com/your-username/易标极速版/issues)
- **邮箱联系**: contact@yibiao.pro

---

<p align="center">
  ⭐ 如果这个项目对您有帮助，请给我们一个Star支持！
</p>


<p align="center">
  Made with ❤️ by 易标团队
</p>