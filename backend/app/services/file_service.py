"""文件处理服务"""
import aiofiles
import os
from typing import Optional
import PyPDF2
import docx
from fastapi import UploadFile
from ..config import settings


class FileService:
    """文件处理服务"""
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> str:
        """保存上传的文件并返回文件路径"""
        # 创建上传目录
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # 生成文件路径
        file_path = os.path.join(settings.upload_dir, file.filename)
        
        # 异步保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """从PDF文件提取文本"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"PDF文件读取失败: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """从Word文档提取文本"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Word文档读取失败: {str(e)}")
    
    @staticmethod
    async def process_uploaded_file(file: UploadFile) -> str:
        """处理上传的文件并提取文本内容"""
        # 检查文件大小
        content = await file.read()
        if len(content) > settings.max_file_size:
            raise Exception(f"文件大小超过限制 ({settings.max_file_size / 1024 / 1024}MB)")
        
        # 重置文件指针
        await file.seek(0)
        
        # 保存文件
        file_path = await FileService.save_uploaded_file(file)
        
        try:
            # 根据文件类型提取文本
            if file.content_type == "application/pdf":
                text = FileService.extract_text_from_pdf(file_path)
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = FileService.extract_text_from_docx(file_path)
            else:
                raise Exception("不支持的文件类型，请上传PDF或Word文档")
            
            # 清理临时文件
            os.remove(file_path)
            
            return text
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e