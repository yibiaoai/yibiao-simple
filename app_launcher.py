"""应用启动器 - 适配backend结构的统一启动文件"""
import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

# 设置工作目录和模块路径
if getattr(sys, 'frozen', False):
    # 打包后的环境
    if hasattr(sys, '_MEIPASS'):
        base_dir = Path(sys._MEIPASS)
        backend_dir = base_dir / "backend"
    else:
        base_dir = Path(sys.executable).parent
        backend_dir = base_dir / "backend"
else:
    # 开发环境
    base_dir = Path(__file__).parent
    backend_dir = base_dir / "backend"

if backend_dir.exists():
    os.chdir(backend_dir)
    sys.path.insert(0, str(backend_dir))
else:
    print(f"ERROR: backend目录不存在: {backend_dir}")
    input("按回车键退出...")

def main():
    """主函数"""
    print("="*50)
    print("AI写标书助手 - 启动中...")
    print("="*50)
    
    try:
        print("OK: 切换到backend目录")
        print("启动服务器...")
        
        def start_server():
            try:
                import uvicorn
                # 动态导入app.main模块
                try:
                    from app.main import app
                except ImportError as ie:
                    print(f"ERROR: 无法导入app.main: {ie}")
                    print(f"当前工作目录: {os.getcwd()}")
                    print(f"Python路径: {sys.path[:3]}")
                    raise ie
                
                uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
            except Exception as e:
                print(f"ERROR: 服务启动失败: {e}")
                import traceback
                traceback.print_exc()
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
        print("\n完整功能已集成，不要关闭窗口，否则服务会停止")
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