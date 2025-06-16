@echo off
REM TimeVis 项目启动脚本 (Windows)

echo === TimeVis 时间序列预测系统启动脚本 ===

REM 检查Python环境
echo 检查Python环境...
python --version

REM 安装依赖
echo 安装Python依赖...
pip install -r requirements.txt

REM 创建必要目录
echo 创建工作目录...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "workspace" mkdir workspace
if not exist "data\samples" mkdir data\samples
if not exist "data\test" mkdir data\test

REM 生成示例数据
echo 生成示例数据...
cd backend
python generate_data.py
cd ..

REM 设置环境变量
set FLASK_APP=run.py
set FLASK_ENV=development

echo === 启动说明 ===
echo 1. 启动Redis (后台任务队列):
echo    下载并安装Redis for Windows，然后运行 redis-server
echo.
echo 2. 启动Celery Worker (新命令提示符窗口):
echo    cd backend ^&^& python celery_worker.py worker --loglevel=info
echo.
echo 3. 启动Flask后端 (新命令提示符窗口):
echo    cd backend ^&^& python run.py
echo.
echo 4. 访问API文档:
echo    http://localhost:5000/api/health
echo.
echo === 注意事项 ===
echo - 确保已安装Redis for Windows
echo - 确保已安装CUDA环境（如果使用GPU）
echo - 第一次运行可能需要下载Qwen模型文件
echo.
echo 准备就绪！请按照上述说明启动各个服务。

pause
