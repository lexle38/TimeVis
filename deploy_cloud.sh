#!/bin/bash

# TimeVis 云服务器部署脚本
# 支持GPU和CPU环境自动检测

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    TimeVis 云服务器自动部署脚本    ${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}警告: 正在以root用户运行${NC}"
fi

# 检测操作系统
OS=$(uname -s)
echo -e "${BLUE}检测到操作系统: $OS${NC}"

# 检测GPU
check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
        echo -e "${GREEN}检测到 $GPU_COUNT 个GPU设备${NC}"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
        return 0
    else
        echo -e "${YELLOW}未检测到GPU，将使用CPU模式${NC}"
        return 1
    fi
}

# 安装系统依赖
install_system_deps() {
    echo -e "${BLUE}安装系统依赖...${NC}"
    
    if [ "$OS" = "Linux" ]; then
        # 检测Linux发行版
        if [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv git curl wget htop vim
        elif [ -f /etc/redhat-release ]; then
            # CentOS/RHEL
            sudo yum update -y
            sudo yum install -y python3 python3-pip git curl wget htop vim
        fi
    fi
}

# 创建虚拟环境
create_venv() {
    echo -e "${BLUE}创建Python虚拟环境...${NC}"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}虚拟环境创建成功${NC}"
    else
        echo -e "${YELLOW}虚拟环境已存在${NC}"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    echo -e "${GREEN}虚拟环境已激活${NC}"
    
    # 升级pip
    pip install --upgrade pip
}

# 安装Python依赖
install_python_deps() {
    echo -e "${BLUE}安装Python依赖...${NC}"
    
    # 检查GPU支持
    if check_gpu; then
        echo -e "${GREEN}安装GPU版本的PyTorch...${NC}"
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        echo -e "${YELLOW}安装CPU版本的PyTorch...${NC}"
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    fi
    
    # 安装其他依赖
    pip install -r requirements.txt
    
    echo -e "${GREEN}Python依赖安装完成${NC}"
}

# 检查数据文件
check_data() {
    echo -e "${BLUE}检查数据文件...${NC}"
    
    if [ ! -d "data" ]; then
        mkdir -p data
        echo -e "${YELLOW}创建data目录${NC}"
    fi
    
    if [ ! -f "data/weather.csv" ] || [ ! -f "data/electricity.csv" ]; then
        echo -e "${RED}警告: 未找到数据文件${NC}"
        echo -e "${YELLOW}请将 weather.csv 和 electricity.csv 放入 data/ 目录${NC}"
        return 1
    else
        echo -e "${GREEN}数据文件检查通过${NC}"
        echo "Weather数据大小: $(du -h data/weather.csv | cut -f1)"
        echo "Electricity数据大小: $(du -h data/electricity.csv | cut -f1)"
        return 0
    fi
}

# 运行数据处理
run_data_processing() {
    echo -e "${BLUE}开始数据处理...${NC}"
    python data_processing.py
    echo -e "${GREEN}数据处理完成${NC}"
}

# 运行模型训练
run_model_training() {
    echo -e "${BLUE}开始模型训练...${NC}"
    
    # 训练LSTM模型
    echo -e "${YELLOW}训练LSTM模型...${NC}"
    python model_training.py --model lstm --epochs 50 --batch_size 64
    
    # 训练Transformer模型
    echo -e "${YELLOW}训练Transformer模型...${NC}"
    python model_training.py --model transformer --epochs 30 --batch_size 32
    
    echo -e "${GREEN}模型训练完成${NC}"
}

# 启动服务
start_services() {
    echo -e "${BLUE}启动TimeVis服务...${NC}"
    
    # 创建tmux会话
    if command -v tmux &> /dev/null; then
        tmux new-session -d -s timevis
        tmux send-keys -t timevis "source venv/bin/activate" C-m
        tmux send-keys -t timevis "python -m backend.main" C-m
        echo -e "${GREEN}服务已在tmux会话中启动${NC}"
        echo -e "${YELLOW}使用 'tmux attach -t timevis' 查看服务日志${NC}"
    else
        echo -e "${YELLOW}tmux未安装，使用nohup启动服务${NC}"
        nohup python -m backend.main > logs/service.log 2>&1 &
        echo $! > service.pid
        echo -e "${GREEN}服务已后台启动，PID: $(cat service.pid)${NC}"
    fi
}

# 显示部署结果
show_results() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}    TimeVis 部署完成！    ${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo -e "${YELLOW}访问地址:${NC}"
    SERVER_IP=$(curl -s ifconfig.me || echo "YOUR_SERVER_IP")
    echo -e "  Web界面: http://${SERVER_IP}:3000"
    echo -e "  API服务: http://${SERVER_IP}:8000"
    
    echo -e "${YELLOW}常用命令:${NC}"
    echo -e "  查看服务: tmux attach -t timevis"
    echo -e "  停止服务: tmux kill-session -t timevis"
    echo -e "  查看日志: tail -f logs/service.log"
    
    echo -e "${YELLOW}重要文件位置:${NC}"
    echo -e "  训练结果: results/"
    echo -e "  模型文件: models/"
    echo -e "  日志文件: logs/"
}

# 主函数
main() {
    echo -e "${BLUE}开始自动部署...${NC}"
    
    # 检查当前目录
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}错误: 请在TimeVis项目根目录运行此脚本${NC}"
        exit 1
    fi
    
    # 创建必要目录
    mkdir -p results models logs
    
    # 执行部署步骤
    install_system_deps
    create_venv
    install_python_deps
    
    if check_data; then
        run_data_processing
        run_model_training
    else
        echo -e "${YELLOW}跳过数据处理和模型训练，请添加数据文件后手动运行${NC}"
    fi
    
    start_services
    show_results
}

# 处理命令行参数
case "${1:-}" in
    "data")
        source venv/bin/activate 2>/dev/null || true
        run_data_processing
        ;;
    "train")
        source venv/bin/activate 2>/dev/null || true
        run_model_training
        ;;
    "start")
        source venv/bin/activate 2>/dev/null || true
        start_services
        ;;
    "stop")
        tmux kill-session -t timevis 2>/dev/null || true
        if [ -f "service.pid" ]; then
            kill $(cat service.pid) 2>/dev/null || true
            rm service.pid
        fi
        echo -e "${GREEN}服务已停止${NC}"
        ;;
    *)
        main
        ;;
esac
