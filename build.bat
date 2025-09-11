@echo off
chcp 65001
echo ================================================
echo AI写标书助手 - 构建exe
echo ================================================

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo Python未安装或不在PATH中
    pause
    exit /b 1
)

echo 检查Node.js环境...
node --version
if %errorlevel% neq 0 (
    echo Node.js未安装或不在PATH中
    pause
    exit /b 1
)

echo 开始构建...
echo 注意：构建前将自动清理以下文件和文件夹：
echo   - dist/ (PyInstaller输出目录)
echo   - build/ (PyInstaller构建缓存)  
echo   - frontend/build/ (React构建输出)
echo   - backend/static/ (后端静态文件)
echo   - __pycache__/ (Python缓存)
echo   - *.spec (PyInstaller配置文件)
echo.

python build.py

if %errorlevel% eq 0 (
    echo.
    echo ================================================
    echo 构建成功！
    echo exe文件位于: dist\yibiao-simple.exe
    echo ================================================
) else (
    echo.
    echo ================================================
    echo 构建失败！请检查上方的错误信息
    echo ================================================
)

pause