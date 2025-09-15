"""方案扩写相关API路由"""
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from ..models.schemas import FileUploadResponse
from ..services.file_service import FileService
from ..services.docx_parse_service import DocxParseService
from ..services.mapping_service import MappingService


router = APIRouter(prefix="/api/expand", tags=["方案扩写"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_plan_file(
    file: UploadFile = File(...),
    outline: Optional[str] = Form(None),  # 可选：前端提交当前目录，用于对齐
):
    """上传方案文档并读取内容；若为 DOCX 且提供 outline，则按 mapping_service 进行对齐。"""
    try:
        # 与 document.upload 的校验保持一致
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]

        if file.content_type not in allowed_types:
            return FileUploadResponse(
                success=False,
                message="不支持的文件类型，请上传PDF或Word文档"
            )

        # 读取文件内容
        file_content = await FileService.process_uploaded_file(file)

        docx_structure = None
        aligned_outline = None
        if outline:
            import json
            outline_obj = json.loads(outline)

            # 1) 优先：DOCX 结构解析
            structure_for_chunks = None
            if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                try:
                    await file.seek(0)
                    tmp_path = await FileService.save_uploaded_file(file)
                    try:
                        docx_structure = DocxParseService.parse(tmp_path)
                        structure_for_chunks = docx_structure
                    finally:
                        FileService._safe_file_cleanup(tmp_path)
                except Exception:
                    structure_for_chunks = None

            # 2) 兜底：用提取到的纯文本构造段落结构
            if structure_for_chunks is None:
                lines = [ln.strip() for ln in (file_content or '').splitlines()]
                paras = [{"text": ln} for ln in lines if ln]
                structure_for_chunks = {"paragraphs": paras}

            # 3) 构建切块并对齐
            chunks = MappingService.build_chunks(structure_for_chunks)
            mapping = MappingService.map_outline_to_chunks(outline_obj, chunks)
            aligned_outline = MappingService.merge_chunk_alignment_into_outline(outline_obj, chunks, mapping)

        return FileUploadResponse(
            success=True,
            message=f"方案文档 {file.filename} 上传成功",
            file_content=file_content,
            docx_structure=docx_structure,
            aligned_outline=aligned_outline,
        )

    except Exception as e:
        return FileUploadResponse(
            success=False,
            message=f"方案文档处理失败: {str(e)}"
        )



