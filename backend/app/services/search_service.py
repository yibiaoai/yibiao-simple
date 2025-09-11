"""
搜索服务模块
提供基于DuckDuckGo的搜索功能
"""

import asyncio
from typing import List, Dict, Optional
from duckduckgo_search import DDGS
import logging
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import html

LANGCHAIN_AVAILABLE = False
WebBaseLoader = None

# 导入现代化爬虫工具
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from seleniumbase import Driver
    SELENIUMBASE_AVAILABLE = True
except ImportError:
    SELENIUMBASE_AVAILABLE = False

try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

logger = logging.getLogger(__name__)

class SearchService:
    """搜索服务类"""
    
    def __init__(self, max_results: int = 5, safe_search: str = "moderate", region: str = "cn"):
        """
        初始化搜索服务
        
        Args:
            max_results: 最大搜索结果数量
            safe_search: 安全搜索级别 (off, moderate, strict)
            region: 搜索区域 (cn表示中国区域)
        """
        self.max_results = max_results
        self.safe_search = safe_search
        self.region = region
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        执行搜索查询
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数量（可选，覆盖默认设置）
            
        Returns:
            搜索结果列表，包含title、href、body字段
        """
        try:
            ddgs = DDGS()
            results = ddgs.text(
                query,
                max_results=max_results or self.max_results,
                safesearch=self.safe_search,
                region=self.region
            )
            
            # 转换为列表并确保返回格式一致
            search_results = []
            for result in results:
                search_results.append({
                    "title": result.get("title", ""),
                    "href": result.get("href", ""),
                    "body": result.get("body", "")
                })
            
            logger.info(f"搜索完成，查询: {query}, 结果数量: {len(search_results)}")
            return search_results
            
        except Exception as e:
            logger.error(f"搜索出错: {str(e)}")
            raise Exception(f"搜索服务异常: {str(e)}")
    
    async def search_async(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        异步执行搜索查询
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数量（可选，覆盖默认设置）
            
        Returns:
            搜索结果列表
        """
        # 在线程池中执行同步搜索，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.search, query, max_results)
    
    def format_results(self, results: List[Dict[str, str]]) -> str:
        """
        格式化搜索结果为可读文本
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化后的文本结果
        """
        if not results:
            return "未找到相关搜索结果"
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. 标题: {result['title']}\n"
                f"   链接: {result['href']}\n"
                f"   摘要: {result['body']}\n"
            )
        
        return "\n".join(formatted_results)
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        return random.choice(user_agents)

    def _clean_and_format_content(self, content: str, title: str = "") -> str:
        """
        清理和格式化内容为AI友好的markdown格式
        
        Args:
            content: 原始内容
            title: 页面标题
            
        Returns:
            清理和格式化后的markdown内容
        """
        if not content:
            return ""
        
        # 1. 基础清理
        # HTML解码
        content = html.unescape(content)
        
        # 移除多余的空白字符
        content = re.sub(r'[ \t]+', ' ', content)  # 多个空格/制表符合并为单个空格
        content = re.sub(r'\n[ \t]+', '\n', content)  # 行首的空格和制表符
        content = re.sub(r'[ \t]+\n', '\n', content)  # 行尾的空格和制表符
        
        # 2. 段落处理
        # 将多个连续换行符规范化为段落分隔
        content = re.sub(r'\n{3,}', '\n\n', content)  # 3个以上换行符变为2个
        content = re.sub(r'\n\s*\n', '\n\n', content)  # 处理包含空格的空行
        
        # 3. 列表检测和格式化
        lines = content.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    in_list = False
                formatted_lines.append('')
                continue
            
            # 检测列表项（数字、字母、符号开头）
            if re.match(r'^[•·▪▫○●◦‣⁃]\s+', line) or \
               re.match(r'^[0-9]+[.)\]]\s+', line) or \
               re.match(r'^[a-zA-Z][.)\]]\s+', line):
                if not in_list:
                    in_list = True
                    if formatted_lines and formatted_lines[-1]:
                        formatted_lines.append('')
                cleaned_line = re.sub(r'^[•·▪▫○●◦‣⁃0-9a-zA-Z.)\]]+\s*', '', line)
                formatted_lines.append(f"- {cleaned_line}")
            else:
                if in_list:
                    in_list = False
                    formatted_lines.append('')
                formatted_lines.append(line)
        
        content = '\n'.join(formatted_lines)
        
        # 4. 标题处理
        if title and title.strip():
            title_clean = title.strip()
            # 如果内容不是以标题开始，添加主标题
            if not content.startswith(title_clean) and not content.startswith('# '):
                content = f"# {title_clean}\n\n{content}"
        
        # 5. 引用和特殊格式处理
        # 检测可能的引用内容（缩进的段落）
        content = re.sub(r'\n([ ]{4,}|\t+)([^\n]+)', r'\n> \2', content)
        
        # 6. 代码块检测（简单的启发式）
        # 检测可能的代码行（包含特定符号密度高的行）
        lines = content.split('\n')
        formatted_lines = []
        code_indicators = ['{', '}', '(', ')', ';', '=', '<', '>', '/', '\\']
        
        for line in lines:
            if line.strip():
                # 如果一行中编程符号占比超过20%，可能是代码
                code_char_count = sum(1 for char in line if char in code_indicators)
                if len(line.strip()) > 10 and code_char_count / len(line.strip()) > 0.2:
                    formatted_lines.append(f"`{line.strip()}`")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        content = '\n'.join(formatted_lines)
        
        # 7. 智能段落重组
        # 检测可能是同一段落被错误分割的情况
        lines = content.split('\n')
        merged_lines = []
        current_paragraph = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    merged_lines.append(current_paragraph)
                    current_paragraph = ""
                merged_lines.append("")
            else:
                # 如果当前行看起来是段落的延续（不以大写字母或标点开始，且前一段不以句号结束）
                if (current_paragraph and 
                    not re.match(r'^[A-Z•·▪▫○●#\-\d]', line) and 
                    not current_paragraph.endswith(('.', '!', '?', ':'))):
                    current_paragraph += " " + line
                else:
                    if current_paragraph:
                        merged_lines.append(current_paragraph)
                    current_paragraph = line
        
        if current_paragraph:
            merged_lines.append(current_paragraph)
        
        content = '\n'.join(merged_lines)
        
        # 8. 最终清理
        # 移除开头和结尾的多余空白
        content = content.strip()
        
        # 确保段落间的间距一致
        content = re.sub(r'\n\n+', '\n\n', content)
        
        # 移除开头的多余空行
        content = re.sub(r'^\n+', '', content)
        
        # 9. 长度检查和优化
        # 如果内容太长，尝试提取主要段落
        if len(content) > 5000:
            paragraphs = content.split('\n\n')
            # 优先保留较长的段落（通常包含更多有用信息）
            meaningful_paragraphs = [p for p in paragraphs if len(p.strip()) > 50]
            if meaningful_paragraphs:
                content = '\n\n'.join(meaningful_paragraphs[:10])  # 取前10个有意义的段落
        
        return content

    def _extract_content_with_requests(self, url: str, max_chars: int) -> Dict[str, str]:
        """
        使用requests和BeautifulSoup提取网页内容
        
        Args:
            url: 要读取的网页链接
            max_chars: 最大字符数限制
            
        Returns:
            包含url、title、content的字典
        """

        try:
            # 设置请求头，模拟浏览器访问
            user_agent = self._get_random_user_agent()
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'Connection': 'keep-alive',
            }
            
            # 创建会话并发送请求
            session = requests.Session()
            session.headers.update(headers)
            
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            response = session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else url.split('/')[-1]
            
            # 移除不需要的元素
            unwanted_tags = ["script", "style", "link", "meta", "noscript", "iframe", "embed", "object"]
            for tag_name in unwanted_tags:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # 优先从主要内容区域提取文本
            content = ""
            
            # 尝试从常见的主内容选择器中提取
            main_selectors = [
                # 知乎特定选择器
                '.QuestionHeader-title', '.RichContent-inner', '.AnswerItem-content', '.QuestionAnswer-content',
                # 微信公众号
                '#js_content', '.rich_media_content',
                # 通用选择器
                '.content', '.main-content', '.article-content', '.post-content',
                'main', 'article', '.entry-content', '.rich-text',
                '#content', '#main', '.question-content', '.answer-content',
                # 博客平台
                '.post-body', '.article-body', '.content-body'
            ]
            
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    content = main_content.get_text(separator='\n', strip=True)
                    if len(content) > 100:  # 如果找到较长内容就使用
                        break
            
            # 如果主内容区域没有找到足够内容，尝试从body提取
            if len(content) < 100:
                body = soup.find('body')
                if body:
                    # 移除导航、页脚等非主要内容
                    for tag in body.find_all(['nav', 'header', 'footer', 'aside', 'form']):
                        tag.decompose()
                    content = body.get_text(separator=' ', strip=True)
            
            # 如果内容仍然太短，获取所有可见文本
            if len(content) < 50:
                content = soup.get_text(separator=' ', strip=True)
            
            # 使用新的清理和格式化函数
            if content:
                content = self._clean_and_format_content(content, title)
            
            # 限制内容长度
            if len(content) > max_chars:
                content = content[:max_chars] + "...(内容已截断)"
            
            logger.info(f"成功读取网页内容: {url}, 标题: {title}, 内容长度: {len(content)}")
            
            return {
                "url": url,
                "title": title,
                "content": content
            }
            
        except requests.RequestException as e:
            logger.error(f"请求网页失败 {url}: {str(e)}")
            raise Exception(f"无法访问网页: {str(e)}")
        except Exception as e:
            logger.error(f"解析网页内容失败 {url}: {str(e)}")
            raise Exception(f"解析网页内容失败: {str(e)}")

    async def _extract_with_playwright(self, url: str, max_chars: int) -> Dict[str, str]:
        """
        使用Playwright提取网页内容（支持JavaScript渲染）
        
        Args:
            url: 要读取的网页链接
            max_chars: 最大字符数限制
            
        Returns:
            包含url、title、content的字典
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright未安装")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                # 设置额外的隐身属性
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)
                
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # 等待内容加载
                await page.wait_for_timeout(3000)
                
                # 获取标题
                title = await page.title()
                
                # 获取主要内容
                content = ""
                
                # 尝试从主内容区域获取文本
                main_selectors = [
                    '.QuestionHeader-title, .RichContent-inner',  # 知乎
                    '#js_content',  # 微信公众号
                    'main, article, .content, .main-content',  # 通用
                ]
                
                for selector in main_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            contents = []
                            for element in elements[:3]:  # 最多取3个元素
                                text = await element.inner_text()
                                if text and len(text.strip()) > 50:
                                    contents.append(text.strip())
                            if contents:
                                content = '\n\n'.join(contents)
                                break
                    except:
                        continue
                
                # 如果没有找到主内容，获取body文本
                if len(content) < 100:
                    try:
                        body = await page.query_selector('body')
                        if body:
                            content = await body.inner_text()
                    except:
                        pass
                
                await browser.close()
                
                # 使用新的清理和格式化函数
                if content:
                    content = self._clean_and_format_content(content, title)
                    if len(content) > max_chars:
                        content = content[:max_chars] + "...(内容已截断)"
                
                logger.info(f"Playwright成功读取: {url}, 标题: {title}, 内容长度: {len(content)}")
                
                return {
                    "url": url,
                    "title": title or "网页内容",
                    "content": content or "未能提取到内容"
                }
                
        except Exception as e:
            logger.error(f"Playwright读取失败 {url}: {str(e)}")
            raise Exception(f"Playwright提取失败: {str(e)}")

    def _extract_with_seleniumbase(self, url: str, max_chars: int) -> Dict[str, str]:
        """
        使用SeleniumBase提取网页内容（内置反检测）
        
        Args:
            url: 要读取的网页链接
            max_chars: 最大字符数限制
            
        Returns:
            包含url、title、content的字典
        """
        if not SELENIUMBASE_AVAILABLE:
            raise Exception("SeleniumBase未安装")
        
        try:
            with Driver(uc=True, headless=True) as driver:
                driver.get(url)
                driver.sleep(3)  # 等待页面加载
                
                # 获取标题
                title = driver.get_title()
                
                # 获取内容
                content = ""
                
                # 尝试从主内容区域获取
                main_selectors = [
                    '.QuestionHeader-title, .RichContent-inner',  # 知乎
                    '#js_content',  # 微信公众号
                    'main, article, .content, .main-content',  # 通用
                ]
                
                for selector in main_selectors:
                    try:
                        elements = driver.find_elements(selector)
                        if elements:
                            contents = []
                            for element in elements[:3]:
                                text = element.text
                                if text and len(text.strip()) > 50:
                                    contents.append(text.strip())
                            if contents:
                                content = '\n\n'.join(contents)
                                break
                    except:
                        continue
                
                # 如果没有找到，获取body内容
                if len(content) < 100:
                    try:
                        content = driver.find_element('body').text
                    except:
                        pass
                
                # 使用新的清理和格式化函数
                if content:
                    content = self._clean_and_format_content(content, title)
                    if len(content) > max_chars:
                        content = content[:max_chars] + "...(内容已截断)"
                
                logger.info(f"SeleniumBase成功读取: {url}, 标题: {title}, 内容长度: {len(content)}")
                
                return {
                    "url": url,
                    "title": title or "网页内容",
                    "content": content or "未能提取到内容"
                }
                
        except Exception as e:
            logger.error(f"SeleniumBase读取失败 {url}: {str(e)}")
            raise Exception(f"SeleniumBase提取失败: {str(e)}")

    def load_url_content(self, url: str, max_chars: int = 5000) -> Dict[str, str]:
        """
        读取链接内容，使用多种策略：requests -> Playwright -> SeleniumBase
        
        Args:
            url: 要读取的网页链接
            max_chars: 最大字符数限制
            
        Returns:
            包含url、title、content的字典，如果失败抛出异常
        """
        errors = []
        
        # 策略1: 使用requests+BeautifulSoup（默认首选）
        try:
            return self._extract_content_with_requests(url, max_chars)
        except Exception as e:
            errors.append(f"Requests: {str(e)}")
            logger.warning(f"Requests失败，尝试下一种方法: {str(e)}")
        
        # 策略2: 尝试Playwright（处理JavaScript渲染的网站）
        if PLAYWRIGHT_AVAILABLE:
            try:
                # 需要在async环境中运行
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(self._extract_with_playwright(url, max_chars))
                return result
            except Exception as e:
                errors.append(f"Playwright: {str(e)}")
                logger.warning(f"Playwright失败，尝试下一种方法: {str(e)}")
        
        # 策略3: 尝试SeleniumBase（最后的选择，资源消耗大）
        if SELENIUMBASE_AVAILABLE:
            try:
                return self._extract_with_seleniumbase(url, max_chars)
            except Exception as e:
                errors.append(f"SeleniumBase: {str(e)}")
                logger.warning(f"SeleniumBase失败: {str(e)}")
        
        # 所有策略都失败了
        logger.error(f"所有提取策略都失败: {url}, 错误: {errors}")
        raise Exception(f"所有内容提取方法都失败了。尝试的方法: {', '.join(errors)}")
    
    async def load_url_content_async(self, url: str, max_chars: int = 5000) -> Dict[str, str]:
        """
        异步读取链接内容
        
        Args:
            url: 要读取的网页链接
            max_chars: 最大字符数限制
            
        Returns:
            包含url、title、content的字典
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.load_url_content, url, max_chars)
    

# 创建默认搜索服务实例
search_service = SearchService(max_results=5, safe_search="moderate", region="cn")
