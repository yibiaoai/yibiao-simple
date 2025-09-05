"""
搜索功能路由模块
提供搜索API接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import logging

from ..services.search_service import search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["搜索功能"])

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    max_results: Optional[int] = 5
    safe_search: Optional[str] = "moderate"
    region: Optional[str] = "cn"

class SearchResult(BaseModel):
    """搜索结果模型"""
    title: str
    href: str
    body: str

class SearchResponse(BaseModel):
    """搜索响应模型"""
    success: bool
    message: str
    results: List[SearchResult]
    total: int

class UrlContentRequest(BaseModel):
    """URL内容请求模型"""
    url: str
    max_chars: Optional[int] = 5000

class UrlContentResponse(BaseModel):
    """URL内容响应模型"""
    success: bool
    message: str
    url: str
    title: str
    content: str

@router.post("/", response_model=SearchResponse, summary="执行搜索")
async def search_documents(request: SearchRequest):
    """
    执行搜索查询
    
    Args:
        request: 搜索请求参数
        
    Returns:
        搜索结果响应
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="搜索关键词不能为空")
        
        # 创建临时搜索服务实例（如果参数与默认不同）
        if request.max_results != 5 or request.safe_search != "moderate" or request.region != "cn":
            from ..services.search_service import SearchService
            temp_service = SearchService(
                max_results=request.max_results,
                safe_search=request.safe_search,
                region=request.region
            )
            results = await temp_service.search_async(request.query)
        else:
            results = await search_service.search_async(request.query, request.max_results)
        
        # 转换为响应模型
        search_results = [
            SearchResult(
                title=result["title"],
                href=result["href"],
                body=result["body"]
            ) for result in results
        ]
        
        return SearchResponse(
            success=True,
            message=f"搜索完成，共找到 {len(search_results)} 条结果",
            results=search_results,
            total=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"搜索API异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索服务异常: {str(e)}")

@router.get("/", response_model=SearchResponse, summary="执行搜索（GET方式）")
async def search_documents_get(
    query: str = Query(..., description="搜索关键词"),
    max_results: int = Query(5, description="最大结果数量", ge=1, le=20),
    safe_search: str = Query("moderate", description="安全搜索级别"),
    region: str = Query("cn", description="搜索区域")
):
    """
    执行搜索查询（GET方式）
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数量
        safe_search: 安全搜索级别
        region: 搜索区域
        
    Returns:
        搜索结果响应
    """
    request = SearchRequest(
        query=query,
        max_results=max_results,
        safe_search=safe_search,
        region=region
    )
    return await search_documents(request)

@router.post("/formatted", summary="获取格式化搜索结果")
async def search_formatted(request: SearchRequest):
    """
    执行搜索并返回格式化的文本结果
    
    Args:
        request: 搜索请求参数
        
    Returns:
        格式化的搜索结果文本
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="搜索关键词不能为空")
        
        # 创建临时搜索服务实例（如果参数与默认不同）
        if request.max_results != 5 or request.safe_search != "moderate" or request.region != "cn":
            from ..services.search_service import SearchService
            temp_service = SearchService(
                max_results=request.max_results,
                safe_search=request.safe_search,
                region=request.region
            )
            results = await temp_service.search_async(request.query)
            formatted_text = temp_service.format_results(results)
        else:
            results = await search_service.search_async(request.query, request.max_results)
            formatted_text = search_service.format_results(results)
        
        return {
            "success": True,
            "message": "搜索完成",
            "formatted_results": formatted_text
        }
        
    except Exception as e:
        logger.error(f"格式化搜索API异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索服务异常: {str(e)}")

@router.post("/load-url", response_model=UrlContentResponse, summary="读取URL内容")
async def load_url_content(request: UrlContentRequest):
    """
    读取网页链接内容
    
    支持大部分网站的内容提取，对于有反爬虫保护的网站（如知乎）会提供替代方案建议。
    
    Args:
        request: URL内容请求参数
        
    Returns:
        URL内容响应
    """
    try:
        if not request.url.strip():
            raise HTTPException(status_code=400, detail="URL不能为空")
        
        # 验证URL格式
        if not request.url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="URL格式不正确，必须以http://或https://开头")
        
        try:
            result = await search_service.load_url_content_async(request.url, request.max_chars)
            
            # 成功获取内容
            return UrlContentResponse(
                success=True,
                message="URL内容读取完成",
                url=result["url"],
                title=result["title"],
                content=result["content"]
            )
        except Exception as content_error:
            # 内容提取失败，返回失败响应
            logger.error(f"URL内容提取失败 {request.url}: {str(content_error)}")
            return UrlContentResponse(
                success=False,
                message="URL内容读取失败",
                url=request.url,
                title="内容读取失败",
                content=f"无法获取该页面的内容。错误信息：{str(content_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL内容读取API系统异常: {str(e)}")
        return UrlContentResponse(
            success=False,
            message="系统异常",
            url=request.url,
            title="系统错误",
            content=f"读取URL时发生系统错误：{str(e)}"
        )