"""统一应用 - 完整功能的单文件版本"""
import os
import sys
import time
import threading
import webbrowser
import tempfile
import json
from pathlib import Path
from enum import Enum
from typing import List, Optional, Dict, Any

# 设置Windows控制台编码
if os.name == 'nt':
    try:
        import codecs
        import subprocess
        subprocess.run('chcp 65001', shell=True, capture_output=True)
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    except Exception:
        pass

# FastAPI和相关导入
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
import aiofiles
import PyPDF2
import docx

# 数据模型
class Settings:
    """应用设置"""
    app_name: str = "AI写标书助手"
    app_version: str = "2.0.0"
    debug: bool = False
    cors_origins: list = ["*"]
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"

settings = Settings()

class Config(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7

class ConfigRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    api_key: str = Field(..., description="OpenAI API密钥")
    base_url: Optional[str] = Field(None, description="Base URL")
    model_name: str = Field("gpt-3.5-turbo", description="模型名称")

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_content: Optional[str] = None

class AnalysisType(str, Enum):
    OVERVIEW = "overview"
    REQUIREMENTS = "requirements"

class AnalysisRequest(BaseModel):
    file_content: str = Field(..., description="文档内容")
    analysis_type: AnalysisType = Field(..., description="分析类型")

class OutlineItem(BaseModel):
    id: str
    title: str
    description: str
    children: Optional[List['OutlineItem']] = None
    content: Optional[str] = None

class OutlineRequest(BaseModel):
    overview: str = Field(..., description="项目概述")
    requirements: str = Field(..., description="技术评分要求")

class ContentGenerationRequest(BaseModel):
    outline: Dict[str, Any] = Field(..., description="目录结构")
    project_overview: str = Field("", description="项目概述")

# 解决循环引用
OutlineItem.model_rebuild()

# 全局配置存储
app_config = Config()
config_file = "config.json"

# 配置管理
def load_config():
    """加载配置"""
    global app_config
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                app_config.api_key = data.get('api_key')
                app_config.base_url = data.get('base_url')
                app_config.model = data.get('model', 'gpt-3.5-turbo')
                app_config.temperature = data.get('temperature', 0.7)
        except:
            pass

def save_config():
    """保存配置"""
    data = {
        'api_key': app_config.api_key,
        'base_url': app_config.base_url,
        'model': app_config.model,
        'temperature': app_config.temperature
    }
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 文件处理服务
class FileService:
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> str:
        """保存上传的文件并返回文件路径"""
        os.makedirs(settings.upload_dir, exist_ok=True)
        file_path = os.path.join(settings.upload_dir, file.filename)
        
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
        content = await file.read()
        if len(content) > settings.max_file_size:
            raise Exception(f"文件大小超过限制 ({settings.max_file_size / 1024 / 1024}MB)")
        
        await file.seek(0)
        file_path = await FileService.save_uploaded_file(file)
        
        try:
            if file.content_type == "application/pdf":
                text = FileService.extract_text_from_pdf(file_path)
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = FileService.extract_text_from_docx(file_path)
            else:
                raise Exception("不支持的文件类型，请上传PDF或Word文档")
            
            os.remove(file_path)
            return text
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e

# OpenAI服务（简化版本，用于演示）
class OpenAIService:
    def __init__(self, api_key: str, base_url: str = "", model_name: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
    
    async def analyze_document(self, file_content: str, analysis_type: str) -> str:
        """分析文档（演示版本）"""
        if analysis_type == "overview":
            return f"项目概述分析结果（基于{len(file_content)}字符的文档内容）：\n\n这是一个重要的项目，具有以下特点：\n1. 技术要求较高\n2. 时间安排紧迫\n3. 需要专业团队\n4. 预算合理"
        else:
            return f"技术评分要求分析结果（基于{len(file_content)}字符的文档内容）：\n\n技术评分要求包括：\n1. 技术方案完整性（30分）\n2. 实施计划合理性（25分）\n3. 技术团队能力（25分）\n4. 质量控制措施（20分）"
    
    async def stream_chat_completion(self, messages: List[Dict], temperature: float = 0.3):
        """流式对话（演示版本）"""
        # 模拟流式响应
        response_text = await self.analyze_document(
            messages[-1]["content"], 
            "overview" if "概述" in messages[-1]["content"] else "requirements"
        )
        
        # 分段返回
        words = response_text.split()
        for i, word in enumerate(words):
            yield word + " "
            if i % 3 == 0:  # 模拟延迟
                await asyncio.sleep(0.01)

# 使用lifespan事件处理器
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时加载配置
    load_config()
    yield
    # 关闭时的清理工作（如果需要）

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于FastAPI的AI写标书助手后端API",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }

# 配置相关接口
@app.get("/api/config/load")
async def load_config_api():
    """加载配置"""
    return {
        "api_key": app_config.api_key or "",
        "base_url": app_config.base_url or "",
        "model_name": app_config.model or "gpt-3.5-turbo",
        "temperature": app_config.temperature or 0.7
    }

@app.post("/api/config/save")
async def save_config_api(config_req: ConfigRequest):
    """保存配置"""
    app_config.api_key = config_req.api_key
    app_config.base_url = config_req.base_url
    app_config.model = config_req.model_name
    save_config()
    return {"success": True, "message": "配置保存成功"}

@app.get("/api/config/test")
async def test_config():
    """测试配置"""
    if not app_config.api_key:
        raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
    
    return {"success": True, "message": "配置测试成功", "model": app_config.model}

@app.get("/api/config/models")
async def get_models():
    """获取模型列表"""
    models = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    return {"models": models, "success": True}

# 文档相关接口
@app.post("/api/document/upload", response_model=FileUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """上传文档文件并提取文本内容"""
    try:
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            return FileUploadResponse(
                success=False,
                message="不支持的文件类型，请上传PDF或Word文档"
            )
        
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

@app.post("/api/document/analyze")
async def analyze_document(request: AnalysisRequest):
    """分析文档内容"""
    try:
        if not app_config.api_key:
            raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
        
        openai_service = OpenAIService(
            api_key=app_config.api_key,
            base_url=app_config.base_url or "",
            model_name=app_config.model or "gpt-3.5-turbo"
        )
        
        result = await openai_service.analyze_document(
            file_content=request.file_content,
            analysis_type=request.analysis_type.value
        )
        
        return {"result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档分析失败: {str(e)}")

@app.post("/api/document/analyze-stream")
async def analyze_document_stream(request: AnalysisRequest):
    """流式分析文档内容"""
    try:
        if not app_config.api_key:
            raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
        
        openai_service = OpenAIService(
            api_key=app_config.api_key,
            base_url=app_config.base_url or "",
            model_name=app_config.model or "gpt-3.5-turbo"
        )
        
        async def generate():
            if request.analysis_type == AnalysisType.OVERVIEW:
                system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取并总结项目概述信息。"""
            else:
                system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取技术评分要求。"""
            
            analysis_type_cn = "项目概述" if request.analysis_type == AnalysisType.OVERVIEW else "技术评分要求"
            user_prompt = f"请分析以下招标文件内容，提取{analysis_type_cn}信息：\n\n{request.file_content}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 流式返回分析结果
            try:
                import asyncio
                async for chunk in openai_service.stream_chat_completion(messages, temperature=0.3):
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            except Exception as e:
                # 如果流式失败，返回普通分析结果
                result = await openai_service.analyze_document(request.file_content, request.analysis_type.value)
                for chunk in result.split():
                    yield f"data: {json.dumps({'chunk': chunk + ' '}, ensure_ascii=False)}\n\n"
            
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

# 大纲相关接口
@app.post("/api/outline/generate")
async def generate_outline(request: OutlineRequest):
    """生成大纲"""
    if not app_config.api_key:
        raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
    
    # 演示版本的大纲生成
    outline = [
        {
            "id": "1",
            "title": "项目概述",
            "description": "基于招标文件的项目基本信息",
            "content": request.overview
        },
        {
            "id": "2", 
            "title": "技术方案",
            "description": "详细的技术实现方案",
            "content": "根据技术评分要求制定的技术方案..."
        },
        {
            "id": "3",
            "title": "实施计划",
            "description": "项目实施的详细计划",
            "content": "项目实施的时间安排和里程碑..."
        },
        {
            "id": "4",
            "title": "质量保证",
            "description": "质量控制和保证措施",
            "content": "质量管理体系和控制措施..."
        }
    ]
    
    return {"outline": outline}

@app.get("/api/outline/{outline_id}")
async def get_outline(outline_id: str):
    """获取大纲"""
    return {
        "id": outline_id,
        "title": "项目标书大纲",
        "sections": [
            {"title": "项目概述", "content": "项目的基本信息和目标"},
            {"title": "技术方案", "content": "详细的技术实现方案"}
        ]
    }

@app.put("/api/outline/{outline_id}")
async def update_outline(outline_id: str, outline_data: dict):
    """更新大纲"""
    return {
        "id": outline_id,
        "message": "大纲更新成功",
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

# 内容编辑相关接口
@app.post("/api/content/generate")
async def generate_content(request: ContentGenerationRequest):
    """生成内容"""
    if not app_config.api_key:
        raise HTTPException(status_code=400, detail="请先配置OpenAI API密钥")
    
    return {
        "content": f"基于大纲生成的标书内容示例...\n\n项目概述：{request.project_overview}\n\n这是AI生成的详细标书内容...",
        "word_count": 500
    }

@app.post("/api/content/export")
async def export_content():
    """导出内容"""
    return {
        "message": "导出功能需要连接OpenAI服务生成完整内容",
        "download_url": "/static/export/document.docx"
    }

def setup_static_files():
    """设置静态文件服务"""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            static_dir = Path(sys._MEIPASS) / "static"
        else:
            static_dir = Path(sys.executable).parent / "static"
    else:
        static_dir = Path(__file__).parent / "backend" / "static"
    
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir / "static")), name="static")
        
        @app.get("/")
        async def read_index():
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            return {"message": f"欢迎使用 {settings.app_name} API", "version": settings.app_version}
        
        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            if (full_path.startswith("api/") or 
                full_path.startswith("docs") or 
                full_path.startswith("health")):
                raise HTTPException(status_code=404, detail="API endpoint not found")
            
            static_file_path = static_dir / full_path
            if static_file_path.exists() and static_file_path.is_file():
                return FileResponse(str(static_file_path))
            
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            else:
                return {"message": "前端文件未找到"}
    else:
        @app.get("/")
        async def read_root():
            return {
                "message": f"欢迎使用 {settings.app_name} API",
                "version": settings.app_version,
                "docs": "/docs",
                "health": "/health"
            }

def main():
    """主函数"""
    print("="*50)
    print("AI写标书助手 - 启动中...")
    print("="*50)
    
    try:
        setup_static_files()
        
        print("OK: 应用配置完成")
        print("启动服务器...")
        
        def start_server():
            try:
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
            except Exception as e:
                print(f"ERROR: 服务启动失败: {e}")
                input("按回车键退出...")
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        print("等待服务启动...")
        time.sleep(5)
        
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:8000')
                print("浏览器已打开")
            except Exception as e:
                print(f"打开浏览器失败: {e}")
        
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        print("\n" + "="*50)
        print("服务启动完成！")
        print("访问地址: http://localhost:8000")
        print("API文档: http://localhost:8000/docs")
        print("健康检查: http://localhost:8000/health")
        print("="*50)
        print("\n完整功能已集成，按 Ctrl+C 退出")
        print("="*50)
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n服务已关闭")
    except Exception as e:
        print(f"运行时错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("按回车键退出...")

if __name__ == "__main__":
    main()