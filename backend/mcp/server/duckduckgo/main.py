import asyncio
import json
import sys
import time
from typing import Any, Dict, List, Optional, Literal
from dataclasses import dataclass, asdict
from duckduckgo_search import DDGS

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, 
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)
import mcp.types as types
from mcp.server.stdio import stdio_server

# 配置常量
@dataclass
class Config:
    # 服务端信息
    server_name: str = "zhsama/duckduckgo-mcp-server"
    server_version: str = "0.1.2"
    
    # 速率限制
    rate_limit_per_second: int = 1
    rate_limit_per_month: int = 15000
    
    # 搜索配置
    max_query_length: int = 400
    max_results: int = 20
    default_results: int = 10
    default_safe_search: Literal["strict", "moderate", "off"] = "moderate"

# 搜索结果数据类
@dataclass
class SearchResult:
    title: str
    description: str
    url: str

# 速率限制数据类
@dataclass
class RequestCount:
    second: int = 0
    month: int = 0
    last_reset: float = 0.0

# 全局配置和状态
config = Config()
request_count = RequestCount(last_reset=time.time())

def check_rate_limit() -> None:
    """检查并更新速率限制"""
    global request_count
    now = time.time()
    
    print(f"[DEBUG] Rate limit check - Current counts: {asdict(request_count)}", file=sys.stderr)
    
    # 重置每秒计数器
    if now - request_count.last_reset > 1.0:
        request_count.second = 0
        request_count.last_reset = now
    
    # 检查限制
    if (request_count.second >= config.rate_limit_per_second or 
        request_count.month >= config.rate_limit_per_month):
        error_msg = "Rate limit exceeded"
        print(f"[ERROR] {error_msg}: {asdict(request_count)}", file=sys.stderr)
        raise Exception(error_msg)
    
    # 更新计数器
    request_count.second += 1
    request_count.month += 1

def validate_search_args(args: Dict[str, Any]) -> bool:
    """验证搜索参数"""
    if not isinstance(args, dict):
        return False
    
    query = args.get("query")
    if not isinstance(query, str):
        return False
    
    if len(query) > config.max_query_length:
        return False
    
    return True

async def perform_web_search(
    query: str,
    count: int = None,
    safe_search: Literal["strict", "moderate", "off"] = None
) -> str:
    """执行网络搜索"""
    if count is None:
        count = config.default_results
    if safe_search is None:
        safe_search = config.default_safe_search
        
    print(f'[DEBUG] Performing search - Query: "{query}", Count: {count}, SafeSearch: {safe_search}', 
          file=sys.stderr)
    
    try:
        # 检查速率限制
        check_rate_limit()
        
        # 安全搜索级别映射
        safe_search_map = {
            "strict": "on",
            "moderate": "moderate", 
            "off": "off"
        }
        
        # 使用DDGS进行搜索
        with DDGS() as ddgs:
            search_results = list(ddgs.text(
                query,
                max_results=count,
                safesearch=safe_search_map.get(safe_search, "moderate")
            ))
        
        if not search_results:
            print(f'[INFO] No results found for query: "{query}"', file=sys.stderr)
            return f'# DuckDuckGo 搜索结果\n没有找到与 "{query}" 相关的结果。'
        
        # 转换为SearchResult对象
        print("search_results")
        print(search_results)
        results = []
        for result in search_results:
            results.append(SearchResult(
                title=result.get("title", ""),
                description=result.get("body", result.get("title", "")),
                url=result.get("href", "")
            ))
        
        print(f'[INFO] Found {len(results)} results for query: "{query}"', file=sys.stderr)
        
        # 格式化结果
        return format_search_results(query, results)
        
    except Exception as error:
        print(f'[ERROR] Search failed - Query: "{query}"', file=sys.stderr)
        print(f"[ERROR] Error details: {error}", file=sys.stderr)
        raise

def format_search_results(query: str, results: List[SearchResult]) -> str:
    """格式化搜索结果为Markdown"""
    formatted_results = []
    
    for result in results:
        formatted_result = f"""### {result.title}
{result.description}

🔗 [阅读更多]({result.url})
"""
        formatted_results.append(formatted_result)
    
    formatted_text = "\n\n".join(formatted_results)
    
    return f"""# DuckDuckGo 搜索结果
{query} 的搜索结果（{len(results)}件）

---

{formatted_text}
"""

# 创建服务器实例
server = Server(config.server_name)

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """返回可用工具列表"""
    return [
        Tool(
            name="duckduckgo_web_search",
            description=(
                "Performs a web search using the DuckDuckGo, ideal for general queries, news, articles, and online content. "
                "Use this for broad information gathering, recent events, or when you need diverse web sources. "
                "Supports content filtering and region-specific searches. "
                f"Maximum {config.max_results} results per request."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"Search query (max {config.max_query_length} chars)",
                        "maxLength": config.max_query_length,
                    },
                    "count": {
                        "type": "number", 
                        "description": f"Number of results (1-{config.max_results}, default {config.default_results})",
                        "minimum": 1,
                        "maximum": config.max_results,
                        "default": config.default_results,
                    },
                    "safeSearch": {
                        "type": "string",
                        "description": "SafeSearch level (strict, moderate, off)",
                        "enum": ["strict", "moderate", "off"],
                        "default": config.default_safe_search,
                    },
                },
                "required": ["query"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]):
    """处理工具调用请求"""
    try:
        print(f"[DEBUG] Received tool call request: {json.dumps({'name': name, 'arguments': arguments}, indent=2)}", 
              file=sys.stderr)
        
        if not arguments:
            raise Exception("No arguments provided")
        
        if name == "duckduckgo_web_search":
            if not validate_search_args(arguments):
                raise Exception("Invalid arguments for duckduckgo_web_search")
            
            query = arguments["query"]
            count = arguments.get("count", config.default_results)
            safe_search = arguments.get("safeSearch", config.default_safe_search)
            
            results = await perform_web_search(query, count, safe_search)
            
            return [TextContent(type="text", text=results)]
        else:
            error_msg = f"Unknown tool: {name}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise Exception(error_msg)
            
    except Exception as error:
        print(f"[ERROR] Request handler error: {error}", file=sys.stderr)
        error_text = str(error) if isinstance(error, Exception) else str(error)
        raise error

async def main():
    """启动服务器主函数"""
    try:
        # 运行stdio服务器
        async with stdio_server() as (read_stream, write_stream):
            print("[INFO] DuckDuckGo Search MCP Server running on stdio", file=sys.stderr)
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=config.server_name,
                    server_version=config.server_version,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as error:
        print(f"[FATAL] Failed to start server: {error}", file=sys.stderr)
        sys.exit(1)

# 异常处理
def handle_exception(loop, context):
    """处理未捕获异常"""
    print(f"[FATAL] Uncaught exception: {context}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    # 设置异常处理
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user", file=sys.stderr)
    except Exception as error:
        print(f"[FATAL] Unhandled error: {error}", file=sys.stderr)
        sys.exit(1)