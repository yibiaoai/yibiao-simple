"""后端服务启动脚本"""
import uvicorn
import os

if __name__ == "__main__":
    # 确保在正确的目录中运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )