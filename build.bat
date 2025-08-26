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
python build.py

if %errorlevel% eq 0 (
    echo 构建成功！
    echo exe文件位于: dist\AI写标书助手.exe
) else (
    echo 构建失败！
)

pause