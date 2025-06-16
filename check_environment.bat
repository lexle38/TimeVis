@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ========================================
echo       TimeVis 环境检查工具 (Windows)
echo ========================================
echo.

:: 检查Python
echo 🐍 Python环境检查
python --version >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✓ Python: %%i
) else (
    echo ✗ Python 未安装或不在PATH中
    goto :error
)

python -m pip --version >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=2" %%i in ('python -m pip --version 2^>^&1') do echo ✓ pip: %%i
) else (
    echo ✗ pip 未安装
)

:: 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo ✓ 虚拟环境存在
    call venv\Scripts\activate.bat
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo   虚拟环境Python: %%i
) else (
    echo ⚠ 虚拟环境不存在
)
echo.

:: 检查GPU支持
echo 🚀 GPU支持检查
nvidia-smi >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ 检测到NVIDIA GPU
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
) else (
    echo ⚠ 未检测到GPU或NVIDIA驱动
)
echo.

:: 检查项目文件
echo 📁 项目文件检查
if exist "data_processing.py" (echo ✓ data_processing.py) else (echo ✗ data_processing.py 缺失)
if exist "model_training.py" (echo ✓ model_training.py) else (echo ✗ model_training.py 缺失)
if exist "requirements.txt" (echo ✓ requirements.txt) else (echo ✗ requirements.txt 缺失)
if exist "backend\" (echo ✓ backend目录) else (echo ⚠ backend目录不存在)
if exist "frontend\" (echo ✓ frontend目录) else (echo ⚠ frontend目录不存在)
echo.

:: 检查数据文件
echo 📊 数据文件检查
if exist "data\" (
    echo ✓ data目录存在
    if exist "data\weather.csv" (
        for %%A in ("data\weather.csv") do echo ✓ weather.csv: %%~zA bytes
    ) else (
        echo ✗ weather.csv 不存在
    )
    if exist "data\electricity.csv" (
        for %%A in ("data\electricity.csv") do echo ✓ electricity.csv: %%~zA bytes
    ) else (
        echo ✗ electricity.csv 不存在
    )
) else (
    echo ✗ data目录不存在
)
echo.

:: 检查Python依赖
echo 📦 Python依赖检查
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

python -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>nul || echo ✗ PyTorch 未安装
python -c "import pandas; print('✓ Pandas:', pandas.__version__)" 2>nul || echo ✗ Pandas 未安装
python -c "import numpy; print('✓ NumPy:', numpy.__version__)" 2>nul || echo ✗ NumPy 未安装
python -c "import sklearn; print('✓ Scikit-learn:', sklearn.__version__)" 2>nul || echo ✗ Scikit-learn 未安装
python -c "import matplotlib; print('✓ Matplotlib:', matplotlib.__version__)" 2>nul || echo ✗ Matplotlib 未安装

:: 检查PyTorch GPU支持
python -c "import torch; print('✓ PyTorch CUDA支持:' if torch.cuda.is_available() else '⚠ PyTorch CPU版本')" 2>nul
echo.

:: 检查端口占用
echo 🔌 端口检查
netstat -an | findstr ":8000 " >nul && echo ⚠ 端口 8000 被占用 || echo ✓ 端口 8000 可用
netstat -an | findstr ":3000 " >nul && echo ⚠ 端口 3000 被占用 || echo ✓ 端口 3000 可用
netstat -an | findstr ":8888 " >nul && echo ⚠ 端口 8888 被占用 || echo ✓ 端口 8888 可用
echo.

:: 生成建议
echo 💡 建议和解决方案
if not exist "venv\Scripts\activate.bat" (
    echo 建议: 创建虚拟环境
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python -c "import torch" 2>nul || (
        echo 建议: 安装Python依赖
        echo   pip install -r requirements.txt
    )
)

if not exist "data\weather.csv" (
    echo 建议: 添加数据文件
    echo   将 weather.csv 和 electricity.csv 放入 data\ 目录
)
echo.

echo ========================================
echo 环境检查完成！
echo ========================================
echo.
echo 快速操作:
echo   安装依赖: install_dependencies.bat
echo   启动服务: start_timevis.bat
echo   数据处理: python data_processing.py
echo   模型训练: python model_training.py
echo.

pause
goto :eof

:error
echo.
echo 发现错误，请检查Python安装！
pause
exit /b 1
