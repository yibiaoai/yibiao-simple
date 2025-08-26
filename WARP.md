# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## 项目概述

这是一个基于 Streamlit 和 OpenAI API 的智能标书写作助手，支持自动解析招标文件并生成标书内容。应用具有多步骤工作流界面，包含配置管理、文档解析、目录编辑和正文编辑功能。

## 常用命令

### 开发环境

```bash
# 安装项目依赖
pip install -r requirements.txt

# 运行开发服务器
streamlit run main_app.py

# 运行配置持久化测试
python test_persistence.py
```

### 生产构建

```bash
# 构建 exe 文件（会自动安装依赖和 PyInstaller）
python build.py

# 运行打包后的应用（开发测试用）
python run_app.py
```

### 调试配置

```bash
# 使用 VS Code 调试配置（已配置在 .vscode/launch.json）
# 目前为空配置，可根据需要添加 Streamlit 调试设置
```

## 代码架构

### 应用结构
- **main_app.py** - 主应用入口，管理多步骤工作流和页面路由
- **run_app.py** - 生产环境启动脚本，包含浏览器自动打开逻辑
- **build.py** - PyInstaller 构建脚本，包含完整的依赖和隐式导入配置

### 组件系统 (components/)
- **config_panel.py** - 左侧配置面板，管理 API 配置和本地持久化
- **step_bar.py** - 步骤导航条，处理多步骤工作流的导航
- **styles.py** - 样式管理模块，统一管理CSS样式和主题

### 页面模块 (page_modules/)
- **document_analysis.py** - 标书解析页面（步骤1）
- **outline_edit.py** - 目录编辑页面（步骤2）
- **content_edit.py** - 正文编辑页面（步骤3）

### 关键设计模式

#### 配置管理
- 使用本地 JSON 文件 (`user_config.json`) 进行配置持久化
- 支持 OpenAI API Key、Base URL 和模型名称配置
- 提供模型列表动态获取功能

#### 状态管理
- 使用 Streamlit session_state 管理应用状态
- `current_step` 跟踪当前工作流步骤
- 页面间数据通过 session_state 共享

#### 工作流导航
- 三步骤工作流：标书解析 → 目录编辑 → 正文编辑
- 步骤间导航通过 `get_step_navigation()` 统一处理
- 支持前进/后退导航控制

## 依赖和集成

### 核心依赖
- **streamlit** - Web UI 框架
- **openai** - OpenAI API 集成
- **python-docx** - Word 文档处理
- **PyPDF2** - PDF 文档处理
- **streamlit-option-menu** - 增强的选项菜单组件

### 文件处理
- 支持 .docx 和 .pdf 格式的招标文件上传
- 文档解析功能通过 OpenAI API 进行智能分析

### 打包配置
- 使用 PyInstaller 打包为独立 exe 文件
- 包含完整的 Streamlit 静态资源和运行时组件
- 配置了所有必要的隐式导入模块

## 开发注意事项

### 配置管理
- API 配置通过左侧面板管理，自动保存到本地
- 支持多种 OpenAI 兼容的 API 服务
- 配置加载使用延迟加载策略避免重复读取

### 页面开发
- 每个页面模块应返回包含页面状态的字典
- 使用 session_state 在页面间传递数据
- 遵循现有的组件化结构模式

### 样式管理
- 使用 `components/styles.py` 统一管理所有CSS样式
- `apply_custom_styles()` 优化页面布局，减少留白空间
- `apply_theme_colors()` 管理主题色彩和视觉效果
- 自动隐藏 Streamlit 默认的菜单和 footer 以节省空间

### 打包部署
- build.py 包含完整的 PyInstaller 配置
- 生成的 exe 文件可独立运行，无需 Python 环境
- run_app.py 提供浏览器自动打开功能
