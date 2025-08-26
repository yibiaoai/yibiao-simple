"""构建脚本 - 用于打包exe"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令执行失败: {result.stderr}")
        return False
    print(result.stdout)
    return True

def build_frontend():
    """构建前端"""
    print("="*50)
    print("构建前端...")
    print("="*50)
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("前端目录不存在")
        return False
    
    # 安装依赖
    if not run_command("npm install", cwd=frontend_dir):
        print("安装前端依赖失败")
        return False
    
    # 构建前端
    if not run_command("npm run build", cwd=frontend_dir):
        print("构建前端失败")
        return False
    
    # 复制构建文件到后端静态目录
    build_dir = frontend_dir / "build"
    static_dir = Path("backend") / "static"
    
    if static_dir.exists():
        shutil.rmtree(static_dir)
    
    shutil.copytree(build_dir, static_dir)
    print("前端构建文件已复制到后端静态目录")
    
    return True

def create_requirements():
    """创建打包所需的requirements文件"""
    print("="*50)
    print("创建requirements文件...")
    print("="*50)
    
    requirements = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
openai==1.3.7
python-docx==0.8.11
PyPDF2==3.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
aiofiles==23.2.1
lxml==4.9.3
"""
    
    with open("requirements_build.txt", "w", encoding="utf-8") as f:
        f.write(requirements.strip())
    
    print("requirements_build.txt 已创建")
    return True

def create_spec_file():
    """创建PyInstaller spec文件"""
    print("="*50)
    print("创建PyInstaller spec文件...")
    print("="*50)
    
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

# 项目根目录
project_root = Path.cwd()

# 数据文件
datas = [
    (str(project_root / 'backend' / 'static'), 'static'),
    (str(project_root / 'backend' / 'app' / '__init__.py'), 'app'),
    (str(project_root / 'backend' / 'app' / 'main.py'), 'app'),
    (str(project_root / 'backend' / 'app' / 'config.py'), 'app'),
    (str(project_root / 'backend' / 'app' / 'models'), 'app/models'),
    (str(project_root / 'backend' / 'app' / 'routers'), 'app/routers'),
    (str(project_root / 'backend' / 'app' / 'services'), 'app/services'),
    (str(project_root / 'backend' / 'app' / 'utils'), 'app/utils'),
]

# 隐藏导入
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.server',
    'fastapi',
    'fastapi.staticfiles',
    'fastapi.responses',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'openai',
    'docx',
    'docx.oxml',
    'docx.oxml.ns',
    'PyPDF2',
    'PyPDF2.generic',
    'pydantic',
    'pydantic_settings',
    'multipart',
    'aiofiles',
    'dotenv',
    'json',
    'pathlib',
    'asyncio',
    'lxml',
    'lxml.etree',
    'lxml._elementpath',
]

a = Analysis(
    ['unified_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI写标书助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon=None,
)
"""
    
    with open("app.spec", "w", encoding="utf-8") as f:
        f.write(spec_content.strip())
    
    print("app.spec 已创建")
    return True

def build_exe():
    """构建exe文件"""
    print("="*50)
    print("构建exe文件...")
    print("="*50)
    
    # 安装所需依赖
    print("安装构建依赖...")
    if not run_command("pip install pyinstaller"):
        print("安装PyInstaller失败")
        return False
    
    # 安装应用依赖
    if not run_command("pip install -r requirements_build.txt"):
        print("安装应用依赖失败")
        return False
    
    # 构建exe - 使用更详细的参数
    pyinstaller_cmd = (
        "pyinstaller --onefile --name=\"AI写标书助手\" "
        "--add-data=\"backend/static;static\" "
        "--hidden-import=uvicorn --hidden-import=fastapi --hidden-import=PyPDF2 "
        "--hidden-import=docx --hidden-import=aiofiles --hidden-import=lxml "
        "--console unified_app.py"
    )
    
    if not run_command(pyinstaller_cmd):
        print("构建exe失败")
        return False
    
    print("exe文件构建完成，位于 dist/ 目录中")
    return True

def main():
    """主函数"""
    print("AI写标书助手 - 构建脚本")
    print("="*50)
    
    # 确保在项目根目录
    if not Path("backend").exists() or not Path("frontend").exists():
        print("请在项目根目录运行此脚本")
        return False
    
    # 构建前端
    if not build_frontend():
        return False
    
    # 创建requirements文件
    if not create_requirements():
        return False
    
    # 创建spec文件
    if not create_spec_file():
        return False
    
    # 构建exe
    if not build_exe():
        return False
    
    print("\n" + "="*50)
    print("构建完成！")
    print("exe文件位于: dist/AI写标书助手.exe")
    print("="*50)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)