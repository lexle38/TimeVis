@echo off
chcp 65001
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                        TimeVis 一键启动                         ║
echo ║                    时间序列预测系统自动化脚本                      ║
echo ╚══════════════════════════════════════════════════════════════╝

cd /d "%~dp0"

echo.
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请安装Python 3.8+并重新运行
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 🚀 启动TimeVis系统...
echo.
echo 选择运行模式:
echo 1. 完整流程 (数据处理 + 模型训练)
echo 2. 仅数据处理
echo 3. 仅模型训练
echo 4. 启动Web应用
echo 5. 查看帮助
echo.

set /p choice="请输入选择 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🔄 执行完整流程...
    python quick_start.py
) else if "%choice%"=="2" (
    echo.
    echo 📊 执行数据处理...
    python quick_start.py --data-only
) else if "%choice%"=="3" (
    echo.
    echo 🤖 执行模型训练...
    python quick_start.py --model-only
) else if "%choice%"=="4" (
    echo.
    echo 🌐 启动Web应用...
    echo 请在新的命令行窗口中运行以下命令:
    echo   后端: python backend\app.py
    echo   前端: cd frontend && npm run dev
    pause
) else if "%choice%"=="5" (
    echo.
    echo 📚 帮助信息:
    echo   - 完整流程: 自动执行数据处理和模型训练
    echo   - 仅数据处理: 只处理原始数据，生成训练数据集
    echo   - 仅模型训练: 基于已处理的数据训练模型
    echo   - 启动Web应用: 启动前后端服务
    echo.
    echo 📁 重要文件:
    echo   - QUICK_START.md: 详细启动指南
    echo   - DATA_PROCESSING_GUIDE.md: 数据处理详细文档
    echo   - API_DOCS.md: API接口文档
    echo.
    pause
) else (
    echo ❌ 无效选择
    pause
)

echo.
echo 按任意键退出...
pause >nul
