"""内容相关API路由"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.schemas import ContentGenerationRequest, ChapterContentRequest
from ..services.openai_service import OpenAIService
from ..utils.config_manager import config_manager
import json

router = APIRouter(prefix="/api/content", tags=["内容管理"])


@router.post("/generate")
async def generate_content(request: ContentGenerationRequest):
    """为目录结构生成内容"""
    try:
        # 加载配置
        config = config_manager.load_config()
        
        if not config.get('api_key'):
            raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
        
        # 创建OpenAI服务实例
        openai_service = OpenAIService(
            api_key=config['api_key'],
            base_url=config.get('base_url', ''),
            model_name=config.get('model_name', 'gpt-3.5-turbo')
        )
        
        # 生成内容
        result = await openai_service.generate_content_for_outline(
            outline=request.outline,
            project_overview=request.project_overview
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内容生成失败: {str(e)}")


@router.post("/generate-stream")
async def generate_content_stream(request: ContentGenerationRequest):
    """流式为目录结构生成内容"""
    try:
        # 加载配置
        config = config_manager.load_config()
        
        if not config.get('api_key'):
            raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
        
        # 创建OpenAI服务实例
        openai_service = OpenAIService(
            api_key=config['api_key'],
            base_url=config.get('base_url', ''),
            model_name=config.get('model_name', 'gpt-3.5-turbo')
        )
        
        async def generate():
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'status': 'started', 'message': '开始生成内容...'}, ensure_ascii=False)}\n\n"
                
                # 生成内容
                result = await openai_service.generate_content_for_outline(
                    outline=request.outline,
                    project_overview=request.project_overview
                )
                
                # 发送完成结果
                yield f"data: {json.dumps({'status': 'completed', 'result': result}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                # 发送错误信息
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
            
            # 发送结束信号
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内容生成失败: {str(e)}")


@router.post("/generate-chapter")
async def generate_chapter_content(request: ChapterContentRequest):
    """为单个章节生成内容"""
    try:
        # 加载配置
        config = config_manager.load_config()
        
        if not config.get('api_key'):
            raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
        
        # 创建OpenAI服务实例
        openai_service = OpenAIService(
            api_key=config['api_key'],
            base_url=config.get('base_url', ''),
            model_name=config.get('model_name', 'gpt-3.5-turbo')
        )
        
        # 生成单章节内容
        content = ""
        async for chunk in openai_service._generate_chapter_content(
            chapter=request.chapter,
            parent_chapters=request.parent_chapters,
            sibling_chapters=request.sibling_chapters,
            project_overview=request.project_overview
        ):
            content += chunk
        
        return {"success": True, "content": content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"章节内容生成失败: {str(e)}")


@router.post("/generate-chapter-stream")
async def generate_chapter_content_stream(request: ChapterContentRequest):
    """流式为单个章节生成内容"""
    try:
        # 加载配置
        config = config_manager.load_config()
        
        if not config.get('api_key'):
            raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
        
        # 创建OpenAI服务实例
        openai_service = OpenAIService(
            api_key=config['api_key'],
            base_url=config.get('base_url', ''),
            model_name=config.get('model_name', 'gpt-3.5-turbo')
        )
        
        async def generate():
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'status': 'started', 'message': '开始生成章节内容...'}, ensure_ascii=False)}\n\n"
                
                # 流式生成章节内容
                full_content = ""
                async for chunk in openai_service._generate_chapter_content(
                    chapter=request.chapter,
                    parent_chapters=request.parent_chapters,
                    sibling_chapters=request.sibling_chapters,
                    project_overview=request.project_overview
                ):
                    full_content += chunk
                    # 实时发送内容片段
                    yield f"data: {json.dumps({'status': 'streaming', 'content': chunk, 'full_content': full_content}, ensure_ascii=False)}\n\n"
                
                # 发送完成信号
                yield f"data: {json.dumps({'status': 'completed', 'content': full_content}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                # 发送错误信息
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
            
            # 发送结束信号
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"章节内容生成失败: {str(e)}")