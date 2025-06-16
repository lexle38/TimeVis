#!/bin/bash

# TimeVis 服务停止脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}停止 TimeVis 服务...${NC}"

# 停止tmux会话
if tmux has-session -t timevis 2>/dev/null; then
    tmux kill-session -t timevis
    echo -e "${GREEN}已停止tmux会话${NC}"
fi

# 停止后台进程
if [ -f "service.pid" ]; then
    PID=$(cat service.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo -e "${GREEN}已停止后台服务 (PID: $PID)${NC}"
        sleep 2
        # 强制停止（如果还在运行）
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID
            echo -e "${YELLOW}强制停止服务${NC}"
        fi
    fi
    rm service.pid
fi

# 查找并停止所有相关进程
PIDS=$(pgrep -f "python.*backend.main" 2>/dev/null || true)
if [ ! -z "$PIDS" ]; then
    echo -e "${YELLOW}发现其他相关进程，正在停止...${NC}"
    echo $PIDS | xargs kill 2>/dev/null || true
    sleep 2
    echo $PIDS | xargs kill -9 2>/dev/null || true
fi

echo -e "${GREEN}所有 TimeVis 服务已停止${NC}"
