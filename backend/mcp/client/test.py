import asyncio
import json
import sys
import subprocess
import os
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class DuckDuckGoMCPClient:
    """DuckDuckGo MCP服务端测试客户端"""
    
    def __init__(self):
        self.session = None
        self.server_path = Path(__file__).parent.parent / "server" / "duckduckgo" / "main.py"
    
    async def connect(self):
        """连接到MCP服务端"""
        try:
            print("连接到DuckDuckGo MCP服务端...")
            
            # 检查服务端文件是否存在
            if not self.server_path.exists():
                raise FileNotFoundError(f"服务端文件不存在: {self.server_path}")
            
            # 启动服务端进程
            server_params = StdioServerParameters(
                command="python",
                args=[str(self.server_path)],
                env=None,
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    
                    # 初始化会话
                    await session.initialize()
                    print("成功连接到MCP服务端")
                    
                    # 运行测试
                    await self.run_tests()
                    
        except Exception as e:
            print(f"连接失败: {e}")
            sys.exit(1)
    
    async def run_tests(self):
        """运行所有测试用例"""
        print("\n开始运行测试用例...")
        
        try:
            # 测试1: 获取可用工具列表
            await self.test_list_tools()
            
            # 测试2: 基础搜索测试
            await self.test_basic_search()
            
            # 测试3: 带参数的搜索测试
            await self.test_search_with_params()
            
            # 测试4: 错误处理测试
            await self.test_error_handling()
            
            print("\n所有测试完成!")
            
        except Exception as e:
            print(f"测试运行失败: {e}")
    
    async def test_list_tools(self):
        """测试获取工具列表"""
        print("\n测试1: 获取工具列表")
        
        try:
            tools = await self.session.list_tools()
            print(f"获取到 {len(tools.tools)} 个工具:")
            
            for tool in tools.tools:
                print(f"  工具: {tool.name}: {tool.description}")
                
                # 验证工具schema
                if tool.name == "duckduckgo_web_search":
                    schema = tool.inputSchema
                    print(f"  输入参数: {list(schema.get('properties', {}).keys())}")
                    
        except Exception as e:
            print(f"获取工具列表失败: {e}")
            raise
    
    async def test_basic_search(self):
        """测试基础搜索功能"""
        print("\n测试2: 基础搜索功能")
        
        try:
            result = await self.session.call_tool(
                "duckduckgo_web_search",
                {"query": "Python编程教程"}
            )
            print(result)
            if result.isError:
                print(f"搜索失败: {result.content[0].text}")
            else:
                content = result.content[0].text
                print("搜索成功!")
                print(f"结果长度: {len(content)} 字符")
                
                # 显示前200字符作为预览
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"结果预览:\n{preview}")
                
        except Exception as e:
            print(f"基础搜索测试失败: {e}")
            raise
    
    async def test_search_with_params(self):
        """测试带参数的搜索"""
        print("\n测试3: 带参数搜索")
        
        try:
            result = await self.session.call_tool(
                "duckduckgo_web_search",
                {
                    "query": "机器学习算法",
                    "count": 3,
                    "safeSearch": "strict"
                }
            )
            
            if result.isError:
                print(f"参数化搜索失败: {result.content[0].text}")
            else:
                content = result.content[0].text
                print("参数化搜索成功!")
                
                # 统计结果数量（简单的方式）
                result_count = content.count("### ")
                print(f"返回结果数: {result_count}")
                print(f"内容长度: {len(content)} 字符")
                
        except Exception as e:
            print(f"参数化搜索测试失败: {e}")
            raise
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n测试4: 错误处理")
        
        # 测试4.1: 空查询
        print("  测试空查询...")
        try:
            result = await self.session.call_tool(
                "duckduckgo_web_search",
                {"query": ""}
            )
            if result.isError:
                print("  空查询正确返回错误")
            else:
                print("  空查询应该返回错误，但没有")
        except Exception as e:
            print(f"  空查询正确抛出异常: {type(e).__name__}")
        
        # 测试4.2: 过长查询
        print("  测试超长查询...")
        long_query = "a" * 500  # 超过400字符限制
        try:
            result = await self.session.call_tool(
                "duckduckgo_web_search",
                {"query": long_query}
            )
            if result.isError:
                print("  超长查询正确返回错误")
            else:
                print("  超长查询应该返回错误，但没有")
        except Exception as e:
            print(f"  超长查询正确抛出异常: {type(e).__name__}")
        
        # 测试4.3: 无效工具名
        print("  测试无效工具...")
        try:
            result = await self.session.call_tool(
                "invalid_tool_name",
                {"query": "test"}
            )
            if result.isError:
                print("  无效工具正确返回错误")
            else:
                print("  无效工具应该返回错误，但没有")
        except Exception as e:
            print(f"  无效工具正确抛出异常: {type(e).__name__}")

async def main():
    """主函数"""
    print("DuckDuckGo MCP 客户端测试程序")
    print("=" * 50)
    
    client = DuckDuckGoMCPClient()
    await client.connect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
    except Exception as e:
        print(f"\n程序异常退出: {e}")
        sys.exit(1)