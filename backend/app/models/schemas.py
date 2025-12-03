"""数据模型定义"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ConfigRequest(BaseModel):
    """OpenAI配置请求"""
    model_config = {"protected_namespaces": ()}
    
    api_key: str = Field(..., description="OpenAI API密钥")
    base_url: Optional[str] = Field(None, description="Base URL")
    model_name: str = Field("gpt-3.5-turbo", description="模型名称")


class ConfigResponse(BaseModel):
    """配置响应"""
    success: bool
    message: str


class ModelListResponse(BaseModel):
    """模型列表响应"""
    models: List[str]
    success: bool
    message: str = ""


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    success: bool
    message: str
    file_content: Optional[str] = None
    old_outline: Optional[str] = None


class AnalysisType(str, Enum):
    """分析类型"""
    OVERVIEW = "overview"
    REQUIREMENTS = "requirements"


class AnalysisRequest(BaseModel):
    """文档分析请求"""
    file_content: str = Field(..., description="文档内容")
    analysis_type: AnalysisType = Field(..., description="分析类型")


class OutlineItem(BaseModel):
    """目录项"""
    id: str
    title: str
    description: str
    children: Optional[List['OutlineItem']] = None
    content: Optional[str] = None


# 解决循环引用
OutlineItem.model_rebuild()


class OutlineResponse(BaseModel):
    """目录响应"""
    outline: List[OutlineItem]


class OutlineRequest(BaseModel):
    """目录生成请求"""
    overview: str = Field(..., description="项目概述")
    requirements: str = Field(..., description="技术评分要求")
    uploaded_expand: Optional[bool] = Field(False, description="是否已上传方案扩写文件")
    old_outline: Optional[str] = Field(None, description="上传的方案扩写文件解析出的旧目录JSON")
    old_document: Optional[str] = Field(None, description="上传的方案扩写文件解析出的旧文档")

class ContentGenerationRequest(BaseModel):
    """内容生成请求"""
    outline: Dict[str, Any] = Field(..., description="目录结构")
    project_overview: str = Field("", description="项目概述")


class ChapterContentRequest(BaseModel):
    """单章节内容生成请求"""
    chapter: Dict[str, Any] = Field(..., description="章节信息")
    parent_chapters: Optional[List[Dict[str, Any]]] = Field(None, description="上级章节列表")
    sibling_chapters: Optional[List[Dict[str, Any]]] = Field(None, description="同级章节列表")
    project_overview: str = Field("", description="项目概述")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None


class WordExportRequest(BaseModel):
    """Word导出请求"""
    project_name: Optional[str] = Field(None, description="项目名称")
    project_overview: Optional[str] = Field(None, description="项目概述")
    outline: List[OutlineItem] = Field(..., description="目录结构，包含内容")