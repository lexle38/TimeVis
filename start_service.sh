#!/bin/bash

# TimeVis 快速启动脚本
# 适用于已经完成初始部署的环境

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}启动 TimeVis 服务...${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}未找到虚拟环境，请先运行 ./deploy_cloud.sh${NC}"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查数据文件
if [ ! -f "data/weather.csv" ] || [ ! -f "data/electricity.csv" ]; then
    echo -e "${YELLOW}警告: 数据文件缺失，跳过数据处理${NC}"
else
    echo -e "${GREEN}数据文件检查通过${NC}"
fi

# 创建必要目录
mkdir -p results models logs

# 启动方式选择
case "${1:-tmux}" in
    "tmux")
        if command -v tmux &> /dev/null; then
            tmux kill-session -t timevis 2>/dev/null || true
            tmux new-session -d -s timevis
            tmux send-keys -t timevis "cd $(pwd)" C-m
            tmux send-keys -t timevis "source venv/bin/activate" C-m
            tmux send-keys -t timevis "python -m backend.main" C-m
            echo -e "${GREEN}服务已在tmux会话中启动${NC}"
            echo -e "${YELLOW}使用 'tmux attach -t timevis' 查看服务${NC}"
        else
            echo -e "${YELLOW}tmux未安装，使用nohup模式${NC}"
            nohup python -m backend.main > logs/service.log 2>&1 &
            echo $! > service.pid
            echo -e "${GREEN}服务已后台启动${NC}"
        fi
        ;;
    "direct")
        echo -e "${GREEN}直接启动服务${NC}"
        python -m backend.main
        ;;
    "background")
        nohup python -m backend.main > logs/service.log 2>&1 &
        echo $! > service.pid
        echo -e "${GREEN}服务已后台启动，PID: $(cat service.pid)${NC}"
        ;;
    *)
        echo "用法: $0 [tmux|direct|background]"
        echo "  tmux      - 在tmux会话中启动（默认）"
        echo "  direct    - 直接启动（前台运行）"
        echo "  background - 后台启动"
        exit 1
        ;;
esac

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}TimeVis 服务启动完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Web界面: http://localhost:3000"
echo -e "API服务: http://localhost:8000"
echo -e "API文档: http://localhost:8000/docs"
