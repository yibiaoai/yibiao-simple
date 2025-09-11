"""构建脚本 - 用于打包exe"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import glob

def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令执行失败: {result.stderr}")
        return False
    print(result.stdout)
    return True

def clean_build_files():
    """清理构建相关的文件和文件夹"""
    print("="*50)
    print("清理构建文件...")
    print("="*50)
    
    # 要清理的文件夹列表
    folders_to_clean = [
        "dist",          # PyInstaller输出目录
        "build",         # PyInstaller构建缓存
        "frontend/build", # React构建输出
        "backend/static", # 后端静态文件（前端构建产物）
    ]
    
    # 要清理的文件模式
    files_to_clean = [
        "*.spec",           # PyInstaller spec文件
        "requirements_build.txt",  # 临时requirements文件
    ]
    
    # 清理文件夹
    for folder in folders_to_clean:
        folder_path = Path(folder)
        if folder_path.exists():
            print(f"删除文件夹: {folder}")
            try:
                shutil.rmtree(folder_path)
                print(f"✓ 已删除 {folder}")
            except Exception as e:
                print(f"✗ 删除 {folder} 失败: {e}")
        else:
            print(f"- 文件夹不存在: {folder}")
    
    # 清理文件
    for file_pattern in files_to_clean:
        for file_path in glob.glob(file_pattern):
            try:
                os.remove(file_path)
                print(f"✓ 已删除文件: {file_path}")
            except Exception as e:
                print(f"✗ 删除文件 {file_path} 失败: {e}")
    
    # 清理Python缓存文件
    print("清理Python缓存文件...")
    for root, dirs, files in os.walk("."):
        # 删除__pycache__文件夹
        if "__pycache__" in dirs:
            pycache_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(pycache_path)
                print(f"✓ 已删除: {pycache_path}")
            except Exception as e:
                print(f"✗ 删除 {pycache_path} 失败: {e}")
            dirs.remove("__pycache__")  # 避免继续遍历已删除的目录
        
        # 删除.pyc文件
        for file in files:
            if file.endswith(".pyc"):
                pyc_path = Path(root) / file
                try:
                    pyc_path.unlink()
                    print(f"✓ 已删除: {pyc_path}")
                except Exception as e:
                    print(f"✗ 删除 {pyc_path} 失败: {e}")
    
    # 清理node_modules中的构建缓存（如果存在）
    node_modules_cache = Path("frontend/node_modules/.cache")
    if node_modules_cache.exists():
        try:
            shutil.rmtree(node_modules_cache)
            print(f"✓ 已删除Node.js缓存: {node_modules_cache}")
        except Exception as e:
            print(f"✗ 删除Node.js缓存失败: {e}")
    
    print("文件清理完成！")
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
fastapi==0.116.1
uvicorn[standard]==0.35.0
python-multipart==0.0.20
openai==1.106.1
python-docx==1.2.0
PyPDF2==3.0.1
pydantic==2.11.7
pydantic-settings==2.10.1
python-dotenv==1.1.1
aiofiles==24.1.0
anyio>=4,<5
pdfplumber==0.11.7
pymupdf==1.26.4
docx2python==3.5.0
requests==2.32.3
asyncio-throttle==1.0.2
duckduckgo-search==8.1.1
beautifulsoup4==4.12.3
playwright==1.51.0
seleniumbase==4.33.3
undetected-chromedriver==3.5.5
mcp==1.13.1
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
    'fastapi.routing',
    'fastapi.exceptions',
    'starlette',
    'starlette.middleware',
    'starlette.middleware.cors',
    'starlette.applications',
    'starlette.routing',
    'starlette.responses',
    'starlette.staticfiles',
    'starlette.types',
    'openai',
    'docx',
    'docx.oxml',
    'docx.oxml.ns',
    'PyPDF2',
    'PyPDF2.generic',
    'pdfplumber',
    'pdfplumber.page',
    'pdfplumber.table',
    'pdfplumber.utils',
    'fitz',
    'pymupdf',
    'docx2python',
    'docx2python.iterators',
    'paragraphs',
    'pydantic',
    'pydantic_settings',
    'multipart',
    'aiofiles',
    'dotenv',
    'json',
    'pathlib',
    'asyncio',
    'duckduckgo_search',
    'requests',
    'bs4',
    'beautifulsoup4',
    'playwright',
    'playwright.async_api',
    'playwright.sync_api',
    'seleniumbase',
    'seleniumbase.core',
    'seleniumbase.fixtures',
    'undetected_chromedriver',
    'asyncio_throttle',
]

a = Analysis(
    ['app_launcher.py'],
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
    name='yibiao-simple',
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
    if not run_command(f"{sys.executable} -m pip install pyinstaller"):
        print("安装PyInstaller失败")
        return False
    
    # 安装应用依赖
    if not run_command(f"{sys.executable} -m pip install -r backend/requirements.txt"):
        print("安装应用依赖失败")
        return False
    
    # 构建exe - 使用更详细的参数，增加进程管理相关导入
    pyinstaller_cmd = (
        "pyinstaller --onefile --name=\"yibiao-simple\" "
        "--add-data=\"backend;backend\" "
        "--hidden-import=uvicorn --hidden-import=uvicorn.logging --hidden-import=uvicorn.loops "
        "--hidden-import=uvicorn.loops.auto --hidden-import=uvicorn.protocols "
        "--hidden-import=uvicorn.protocols.http --hidden-import=uvicorn.protocols.http.auto "
        "--hidden-import=uvicorn.protocols.websockets --hidden-import=uvicorn.protocols.websockets.auto "
        "--hidden-import=uvicorn.lifespan --hidden-import=uvicorn.lifespan.on --hidden-import=uvicorn.server "
        "--hidden-import=fastapi --hidden-import=fastapi.staticfiles --hidden-import=fastapi.responses "
        "--hidden-import=fastapi.middleware --hidden-import=fastapi.middleware.cors --hidden-import=fastapi.routing "
        "--hidden-import=fastapi.exceptions --hidden-import=starlette --hidden-import=starlette.middleware "
        "--hidden-import=starlette.middleware.cors --hidden-import=starlette.applications "
        "--hidden-import=starlette.routing --hidden-import=starlette.responses --hidden-import=starlette.staticfiles "
        "--hidden-import=starlette.types --hidden-import=openai --hidden-import=docx --hidden-import=docx.oxml "
        "--hidden-import=docx.oxml.ns --hidden-import=PyPDF2 --hidden-import=PyPDF2.generic "
        "--hidden-import=pdfplumber --hidden-import=pdfplumber.page --hidden-import=pdfplumber.table "
        "--hidden-import=pdfplumber.utils --hidden-import=fitz --hidden-import=pymupdf "
        "--hidden-import=docx2python --hidden-import=docx2python.iterators --hidden-import=paragraphs "
        "--hidden-import=pydantic --hidden-import=pydantic_settings --hidden-import=multipart "
        "--hidden-import=aiofiles --hidden-import=dotenv --hidden-import=json --hidden-import=pathlib "
        "--hidden-import=asyncio --hidden-import=signal --hidden-import=atexit "
        "--hidden-import=duckduckgo_search --hidden-import=requests "
        "--hidden-import=bs4 --hidden-import=beautifulsoup4 "
        "--hidden-import=playwright --hidden-import=playwright.async_api --hidden-import=playwright.sync_api "
        "--hidden-import=seleniumbase --hidden-import=seleniumbase.core --hidden-import=seleniumbase.fixtures "
        "--hidden-import=undetected_chromedriver --hidden-import=asyncio_throttle "
        "--console app_launcher.py"
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
    
    # 清理构建文件
    if not clean_build_files():
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