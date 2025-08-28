# DuckDuckGo MCP 服务端 (Python版本)

这是 DuckDuckGo 搜索的 MCP (Model Context Protocol) 服务端的 Python 实现版本。

## 功能特性

- 🔍 DuckDuckGo 网络搜索
- 🚦 速率限制保护 (每秒1次, 每月15000次)
- 🛡️ 安全搜索级别控制
- 📝 Markdown 格式化结果
- 🎯 参数验证和错误处理

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 直接运行
```bash
python main.py
```

### 作为MCP服务端
服务端通过 stdio 与 MCP 客户端通信。

## 工具接口

### duckduckgo_web_search

执行 DuckDuckGo 网络搜索。

**参数:**
- `query` (必需): 搜索查询词 (最大400字符)
- `count` (可选): 结果数量 (1-20, 默认10)
- `safeSearch` (可选): 安全搜索级别 ("strict", "moderate", "off", 默认"moderate")

**示例:**
```json
{
  "name": "duckduckgo_web_search",
  "arguments": {
    "query": "Python编程教程",
    "count": 5,
    "safeSearch": "moderate"
  }
}
```

## 配置

### 速率限制
- 每秒: 1 次请求
- 每月: 15,000 次请求

### 搜索限制
- 查询长度: 最大 400 字符
- 结果数量: 1-20 条 (默认 10 条)

## 错误处理

- 速率限制超出时抛出异常
- 无效参数时返回错误信息
- 搜索失败时记录详细错误日志

## 日志记录

服务端会向 stderr 输出调试和错误信息：
- `[DEBUG]`: 调试信息
- `[INFO]`: 一般信息
- `[ERROR]`: 错误信息
- `[FATAL]`: 严重错误

## 与 TypeScript 版本的差异

这个 Python 版本完全复制了 TypeScript 版本的功能和行为：
- 相同的配置参数
- 相同的速率限制逻辑
- 相同的错误处理
- 相同的输出格式
- 相同的工具接口定义