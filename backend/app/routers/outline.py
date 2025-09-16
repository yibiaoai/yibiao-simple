"""目录相关API路由"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.schemas import OutlineRequest, OutlineResponse
from ..services.openai_service import OpenAIService
from ..utils.config_manager import config_manager
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
        
        async def generate():
            system_prompt = """你是一个专业的标书编写专家。根据提供的项目概述和技术评分要求，生成投标文件中技术标部分的目录结构。

要求：
1. 目录结构要全面覆盖技术标的所有必要章节
2. 章节名称要专业、准确，符合投标文件规范
3. 一级目录名称要与技术评分要求中的章节名称一致，如果技术评分要求中没有章节名称，则结合技术评分要求中的内容，生成一级目录名称
4. 一共包括三级目录
5. 返回标准JSON格式，包含章节编号、标题、描述和子章节
6. 除了JSON结果外，不要输出任何其他内容

JSON格式要求：
{
  "outline": [
    {
      "id": "1",
      "title": "",
      "description": "",
      "children": [
        {
          "id": "1.1",
          "title": "",
          "description": "",
          "children":[
              {
                "id": "1.1.1",
                "title": "",
                "description": ""
              }
          ]
        }
      ]
    }
  ]
}
"""
            
            user_prompt = f"""请基于以下项目信息生成标书目录结构：

项目概述：
{request.overview}

技术评分要求：
{request.requirements}

请生成完整的技术标目录结构，确保覆盖所有技术评分要点。"""
            
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




