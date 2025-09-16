"""目录相关API路由"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.schemas import OutlineRequest, OutlineResponse
from ..services.openai_service import OpenAIService
from ..utils.config_manager import config_manager
from ..utils import prompt_manager
import json
import asyncio

router = APIRouter(prefix="/api/outline", tags=["目录管理"])


@router.post("/generate")
async def generate_outline(request: OutlineRequest):
    """生成标书目录结构（以SSE流式返回）"""
    try:
        # 加载配置
        config = config_manager.load_config()

        if not config.get('api_key'):
            raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")

        # 创建OpenAI服务实例
        openai_service = OpenAIService()
        
        async def generate():
            # 后台计算主任务
            compute_task = asyncio.create_task(openai_service.generate_outline_v2(
                overview=request.overview,
                requirements=request.requirements
            ))

            # 在等待计算完成期间发送心跳，保持连接（发送空字符串chunk）
            while not compute_task.done():
                yield f"data: {json.dumps({'chunk': ''}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(1)

            # 计算完成
            result = await compute_task

            # 确保为字符串
            if isinstance(result, dict):
                result_str = json.dumps(result, ensure_ascii=False)
            else:
                result_str = str(result)

            # 分片发送实际数据
            chunk_size = 128
            chunk_delay = 0.1  # 每个分片之间增加一点点延迟，增强SSE逐步展示效果
            for i in range(0, len(result_str), chunk_size):
                piece = result_str[i:i+chunk_size]
                yield f"data: {json.dumps({'chunk': piece}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(chunk_delay)
            # 发送结束信号
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"目录生成失败: {str(e)}")


@router.post("/generate-stream")
async def generate_outline_stream(request: OutlineRequest):
    """流式生成标书目录结构"""
    try:
        # 加载配置
        config = config_manager.load_config()

        if not config.get('api_key'):
            raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")

        # 创建OpenAI服务实例
        openai_service = OpenAIService()
        # request.uploadedExpand
        async def generate():
            if request.uploaded_expand:
                system_prompt, user_prompt = prompt_manager.generate_outline_with_old_prompt(request.overview, request.requirements, request.old_outline)
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                full_content = ""
                async for chunk in openai_service.stream_chat_completion(messages, temperature=0.7, response_format={"type": "json_object"}):
                    full_content += chunk
                print(full_content)
                # 流式返回目录生成结果
                # async for chunk in openai_service.stream_chat_completion(messages, temperature=0.7, response_format={"type": "json_object"}):
                #     yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                
                # 发送结束信号
                # yield "data: [DONE]\n\n"
            
            else:
                system_prompt, user_prompt = prompt_manager.generate_outline_prompt(request.overview, request.requirements)
            
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                # 流式返回目录生成结果
                async for chunk in openai_service.stream_chat_completion(messages, temperature=0.7, response_format={"type": "json_object"}):
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                
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
        raise HTTPException(status_code=500, detail=f"目录生成失败: {str(e)}")




