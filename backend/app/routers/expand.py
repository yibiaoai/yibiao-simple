from fastapi import APIRouter, UploadFile, File, HTTPException
from ..models.schemas import FileUploadResponse
from ..services.file_service import FileService
from ..utils import prompt_manager
from ..services.openai_service import OpenAIService

router = APIRouter(prefix="/api/expand", tags=["标书扩写"])


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
        
        # 提取目录
        openai_service = OpenAIService()
        messages = [
            {"role": "system", "content": prompt_manager.read_expand_outline_prompt()},
            {"role": "user", "content": file_content}
        ]
        full_content = ""
        async for chunk in openai_service.stream_chat_completion(messages, temperature=0.7, response_format={"type": "json_object"}):
            full_content += chunk
        return FileUploadResponse(
            success=True,
            message=f"文件 {file.filename} 上传成功",
            file_content=file_content,
            old_outline=full_content
        )
        
    except Exception as e:
        return FileUploadResponse(
            success=False,
            message=f"文件处理失败: {str(e)}"
        )