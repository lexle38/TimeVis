#!/bin/bash

# TimeVis 项目启动脚本

echo "=== TimeVis 时间序列预测系统启动脚本 ==="

# 检查Python环境
echo "检查Python环境..."
python --version

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 创建必要目录
echo "创建工作目录..."
mkdir -p uploads
mkdir -p logs
mkdir -p workspace
mkdir -p data/samples
mkdir -p data/test

# 生成示例数据
echo "生成示例数据..."
cd backend
python generate_data.py

# 设置环境变量
export FLASK_APP=run.py
export FLASK_ENV=development

echo "=== 启动说明 ==="
echo "1. 启动Redis (后台任务队列):"
echo "   redis-server"
echo ""
echo "2. 启动Celery Worker (新终端):"
echo "   cd backend && python celery_worker.py worker --loglevel=info"
echo ""
echo "3. 启动Flask后端 (新终端):"
echo "   cd backend && python run.py"
echo ""
echo "4. 访问API文档:"
echo "   http://localhost:5000/api/health"
echo ""
echo "=== 注意事项 ==="
echo "- 确保已安装Redis"
echo "- 确保已安装CUDA环境（如果使用GPU）"
echo "- 第一次运行可能需要下载Qwen模型文件"
echo ""
echo "准备就绪！请按照上述说明启动各个服务。"
