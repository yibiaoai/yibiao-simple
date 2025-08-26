"""文档处理相关API路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from ..models.schemas import FileUploadResponse, AnalysisRequest, AnalysisType
from ..services.file_service import FileService
from ..services.openai_service import OpenAIService
from ..utils.config_manager import config_manager
import json

router = APIRouter(prefix="/api/document", tags=["文档处理"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """上传文档文件并提取文本内容"""
    try:
        # 检查文件类型
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            return FileUploadResponse(
                success=False,
                message="不支持的文件类型，请上传PDF或Word文档"
            )
        
        # 处理文件并提取文本
        file_content = await FileService.process_uploaded_file(file)
        
        return FileUploadResponse(
            success=True,
            message=f"文件 {file.filename} 上传成功",
            file_content=file_content
        )
        
    except Exception as e:
        return FileUploadResponse(
            success=False,
            message=f"文件处理失败: {str(e)}"
        )


@router.post("/analyze")
async def analyze_document(request: AnalysisRequest):
    """分析文档内容"""
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
        
        # 分析文档
        result = await openai_service.analyze_document(
            file_content=request.file_content,
            analysis_type=request.analysis_type.value
        )
        
        return {"result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档分析失败: {str(e)}")


@router.post("/analyze-stream")
async def analyze_document_stream(request: AnalysisRequest):
    """流式分析文档内容"""
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
            # 构建分析提示词
            if request.analysis_type == AnalysisType.OVERVIEW:
                system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取并总结项目概述信息。
            
请重点关注以下方面：
1. 项目名称和基本信息
2. 项目背景和目的
3. 项目规模和预算
4. 项目时间安排
5. 主要技术特点
6. 关键要求

工作要求：
1. 保持提取信息的全面性和准确性，尽量使用原文内容，不要自己编写
2. 只关注与项目实施有关的内容，不提取商务信息
3. 直接返回整理好的项目概述，除此之外不返回任何其他内容
"""
            else:  # requirements
                system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取技术评分要求,为编写投标文件中的技术方案做准备。
            
请重点关注以下方面：
1. 理解技术评分的意思：用于编写、评比投标文件中技术标的标准，关注技术方案、实施计划、技术能力、质量控制、创新性等内容，避免混淆商务评分（资质、信誉、合同条款）和价格评分（报价金额）
2. 仅提取技术评分项及相关要求，不包括商务、价格及其他
3. 生成内容要确保是从招标文件中提取的，不要自己编写
4. 直接返回整理好的技术评分要求，除此之外不返回任何其他内容
"""
            
            analysis_type_cn = "项目概述" if request.analysis_type == AnalysisType.OVERVIEW else "技术评分要求"
            user_prompt = f"请分析以下招标文件内容，提取{analysis_type_cn}信息：\n\n{request.file_content}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 流式返回分析结果
            async for chunk in openai_service.stream_chat_completion(messages, temperature=0.3):
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
        raise HTTPException(status_code=500, detail=f"文档分析失败: {str(e)}")