@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ========================================
echo     TimeVis 依赖安装脚本 (Windows)
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python 未安装，请先安装Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python 已安装
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo   版本: %%i
echo.

:: 创建虚拟环境
echo 📦 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% == 0 (
        echo ✓ 虚拟环境创建成功
    ) else (
        echo ✗ 虚拟环境创建失败
        pause
        exit /b 1
    )
) else (
    echo ⚠ 虚拟环境已存在
)

:: 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat
echo ✓ 虚拟环境已激活
echo.

:: 升级pip
echo 📈 升级pip...
python -m pip install --upgrade pip
echo.

:: 检测GPU支持
echo 🚀 检测GPU支持...
nvidia-smi >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ 检测到NVIDIA GPU，安装GPU版本的PyTorch
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
) else (
    echo ⚠ 未检测到GPU，安装CPU版本的PyTorch
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
)
echo.

:: 安装其他依赖
echo 📦 安装项目依赖...
pip install -r requirements.txt
if %errorlevel% == 0 (
    echo ✓ 依赖安装完成
) else (
    echo ✗ 依赖安装失败
    pause
    exit /b 1
)
echo.

:: 创建必要目录
echo 📁 创建项目目录...
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "results" mkdir results
if not exist "logs" mkdir logs
echo ✓ 目录创建完成
echo.

:: 验证安装
echo 🔍 验证安装...
python -c "import torch; print('✓ PyTorch:', torch.__version__)" || echo ✗ PyTorch 验证失败
python -c "import pandas; print('✓ Pandas:', pandas.__version__)" || echo ✗ Pandas 验证失败
python -c "import numpy; print('✓ NumPy:', numpy.__version__)" || echo ✗ NumPy 验证失败
python -c "import sklearn; print('✓ Scikit-learn:', sklearn.__version__)" || echo ✗ Scikit-learn 验证失败

:: 检查PyTorch GPU支持
python -c "import torch; print('✓ CUDA支持:' if torch.cuda.is_available() else '⚠ CPU模式')"
echo.

echo ========================================
echo 依赖安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 将数据文件放入 data\ 目录
echo    - weather.csv
echo    - electricity.csv
echo 2. 运行数据处理: python data_processing.py
echo 3. 训练模型: python model_training.py
echo 4. 启动服务: start_timevis.bat
echo.

pause
