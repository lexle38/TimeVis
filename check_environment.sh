#!/bin/bash

# TimeVis 环境检查脚本
# 检查系统环境、依赖、数据文件等

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      TimeVis 环境检查工具      ${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查操作系统
check_os() {
    echo -e "${BLUE}🖥️  操作系统信息${NC}"
    echo "系统: $(uname -s)"
    echo "版本: $(uname -r)"
    echo "架构: $(uname -m)"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "发行版: $NAME $VERSION"
    fi
    echo ""
}

# 检查Python环境
check_python() {
    echo -e "${BLUE}🐍 Python环境${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo -e "${GREEN}✓ Python3: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}✗ Python3 未安装${NC}"
        return 1
    fi
    
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version 2>&1 | cut -d' ' -f2)
        echo -e "${GREEN}✓ pip3: $PIP_VERSION${NC}"
    else
        echo -e "${RED}✗ pip3 未安装${NC}"
        return 1
    fi
    
    # 检查虚拟环境
    if [ -d "venv" ]; then
        echo -e "${GREEN}✓ 虚拟环境存在${NC}"
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            echo "虚拟环境Python: $(python --version 2>&1 | cut -d' ' -f2)"
        fi
    else
        echo -e "${YELLOW}⚠ 虚拟环境不存在${NC}"
    fi
    echo ""
}

# 检查GPU支持
check_gpu() {
    echo -e "${BLUE}🚀 GPU支持${NC}"
    
    if command -v nvidia-smi &> /dev/null; then
        GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
        echo -e "${GREEN}✓ 检测到 $GPU_COUNT 个GPU${NC}"
        nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
        
        # 检查CUDA
        if command -v nvcc &> /dev/null; then
            CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release //' | sed 's/,.*//')
            echo -e "${GREEN}✓ CUDA版本: $CUDA_VERSION${NC}"
        else
            echo -e "${YELLOW}⚠ CUDA未安装或不在PATH中${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ 未检测到GPU或NVIDIA驱动${NC}"
    fi
    echo ""
}

# 检查Python依赖
check_dependencies() {
    echo -e "${BLUE}📦 Python依赖检查${NC}"
    
    if [ -f "requirements.txt" ]; then
        echo -e "${GREEN}✓ requirements.txt 存在${NC}"
        
        # 激活虚拟环境（如果存在）
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        
        # 检查关键依赖
        CRITICAL_DEPS=("torch" "pandas" "numpy" "scikit-learn" "matplotlib")
        
        for dep in "${CRITICAL_DEPS[@]}"; do
            if python -c "import $dep" 2>/dev/null; then
                VERSION=$(python -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "未知")
                echo -e "${GREEN}✓ $dep: $VERSION${NC}"
            else
                echo -e "${RED}✗ $dep 未安装${NC}"
            fi
        done
        
        # 检查PyTorch GPU支持
        if python -c "import torch" 2>/dev/null; then
            CUDA_AVAILABLE=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null)
            if [ "$CUDA_AVAILABLE" = "True" ]; then
                CUDA_VERSION=$(python -c "import torch; print(torch.version.cuda)" 2>/dev/null)
                echo -e "${GREEN}✓ PyTorch CUDA支持: $CUDA_VERSION${NC}"
            else
                echo -e "${YELLOW}⚠ PyTorch CPU版本${NC}"
            fi
        fi
    else
        echo -e "${RED}✗ requirements.txt 不存在${NC}"
    fi
    echo ""
}

# 检查数据文件
check_data() {
    echo -e "${BLUE}📊 数据文件检查${NC}"
    
    if [ -d "data" ]; then
        echo -e "${GREEN}✓ data目录存在${NC}"
        
        # 检查weather.csv
        if [ -f "data/weather.csv" ]; then
            SIZE=$(du -h data/weather.csv | cut -f1)
            LINES=$(wc -l < data/weather.csv)
            echo -e "${GREEN}✓ weather.csv: $SIZE ($LINES 行)${NC}"
        else
            echo -e "${RED}✗ weather.csv 不存在${NC}"
        fi
        
        # 检查electricity.csv
        if [ -f "data/electricity.csv" ]; then
            SIZE=$(du -h data/electricity.csv | cut -f1)
            LINES=$(wc -l < data/electricity.csv)
            echo -e "${GREEN}✓ electricity.csv: $SIZE ($LINES 行)${NC}"
        else
            echo -e "${RED}✗ electricity.csv 不存在${NC}"
        fi
    else
        echo -e "${RED}✗ data目录不存在${NC}"
    fi
    echo ""
}

# 检查项目文件
check_project_files() {
    echo -e "${BLUE}📁 项目文件检查${NC}"
    
    REQUIRED_FILES=("data_processing.py" "model_training.py" "requirements.txt")
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✓ $file${NC}"
        else
            echo -e "${RED}✗ $file 缺失${NC}"
        fi
    done
    
    # 检查后端目录
    if [ -d "backend" ]; then
        echo -e "${GREEN}✓ backend目录${NC}"
    else
        echo -e "${YELLOW}⚠ backend目录不存在${NC}"
    fi
    
    # 检查前端目录
    if [ -d "frontend" ]; then
        echo -e "${GREEN}✓ frontend目录${NC}"
    else
        echo -e "${YELLOW}⚠ frontend目录不存在${NC}"
    fi
    echo ""
}

# 检查端口占用
check_ports() {
    echo -e "${BLUE}🔌 端口检查${NC}"
    
    PORTS=("8000" "3000" "8888")
    
    for port in "${PORTS[@]}"; do
        if netstat -tlnp 2>/dev/null | grep ":$port " > /dev/null; then
            PROCESS=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | head -1)
            echo -e "${YELLOW}⚠ 端口 $port 被占用: $PROCESS${NC}"
        else
            echo -e "${GREEN}✓ 端口 $port 可用${NC}"
        fi
    done
    echo ""
}

# 检查系统资源
check_resources() {
    echo -e "${BLUE}💻 系统资源${NC}"
    
    # CPU信息
    CPU_CORES=$(nproc)
    echo "CPU核心数: $CPU_CORES"
    
    # 内存信息
    if command -v free &> /dev/null; then
        TOTAL_MEM=$(free -h | awk 'NR==2{print $2}')
        FREE_MEM=$(free -h | awk 'NR==2{print $7}')
        echo "总内存: $TOTAL_MEM"
        echo "可用内存: $FREE_MEM"
    fi
    
    # 磁盘空间
    DISK_USAGE=$(df -h . | awk 'NR==2{print $4}')
    echo "可用磁盘空间: $DISK_USAGE"
    
    # 检查swap
    if [ -f /proc/swaps ]; then
        SWAP_SIZE=$(free -h | awk 'NR==3{print $2}')
        if [ "$SWAP_SIZE" != "0B" ]; then
            echo "Swap大小: $SWAP_SIZE"
        else
            echo -e "${YELLOW}⚠ 未配置Swap${NC}"
        fi
    fi
    echo ""
}

# 生成建议
generate_suggestions() {
    echo -e "${BLUE}💡 建议和解决方案${NC}"
    
    # 检查是否需要安装依赖
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}建议: 创建虚拟环境${NC}"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
    fi
    
    # 检查是否需要安装Python包
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        if ! python -c "import torch" 2>/dev/null; then
            echo -e "${YELLOW}建议: 安装Python依赖${NC}"
            echo "  pip install -r requirements.txt"
        fi
    fi
    
    # 检查是否需要添加数据文件
    if [ ! -f "data/weather.csv" ] || [ ! -f "data/electricity.csv" ]; then
        echo -e "${YELLOW}建议: 添加数据文件${NC}"
        echo "  将 weather.csv 和 electricity.csv 放入 data/ 目录"
    fi
    
    # GPU建议
    if ! command -v nvidia-smi &> /dev/null; then
        echo -e "${YELLOW}建议: 安装GPU支持（可选）${NC}"
        echo "  sudo ubuntu-drivers autoinstall"
        echo "  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    fi
    
    echo ""
}

# 主函数
main() {
    check_os
    check_python
    check_gpu
    check_dependencies
    check_data
    check_project_files
    check_ports
    check_resources
    generate_suggestions
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}环境检查完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # 显示快速操作建议
    echo -e "${YELLOW}快速操作:${NC}"
    echo "  完整部署: ./deploy_cloud.sh"
    echo "  启动服务: ./start_service.sh"
    echo "  停止服务: ./stop_service.sh"
    echo "  数据处理: python data_processing.py"
    echo "  模型训练: python model_training.py"
}

# 执行检查
main
