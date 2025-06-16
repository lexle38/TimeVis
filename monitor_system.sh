#!/bin/bash

# TimeVis 系统状态监控脚本
# 监控服务运行状态、资源使用、日志等

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 清屏
clear

# 显示标题
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      TimeVis 系统状态监控      ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 获取当前时间
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
echo -e "${CYAN}监控时间: $CURRENT_TIME${NC}"
echo ""

# 检查服务状态
check_service_status() {
    echo -e "${BLUE}🚀 服务状态${NC}"
    echo "----------------------------------------"
    
    # 检查tmux会话
    if tmux has-session -t timevis 2>/dev/null; then
        echo -e "${GREEN}✓ tmux会话 'timevis' 运行中${NC}"
        
        # 获取会话中的窗口数
        WINDOWS=$(tmux list-windows -t timevis 2>/dev/null | wc -l)
        echo "  会话窗口数: $WINDOWS"
    else
        echo -e "${YELLOW}⚠ tmux会话 'timevis' 未运行${NC}"
    fi
    
    # 检查进程
    PYTHON_PROCS=$(pgrep -f "python.*backend" | wc -l)
    if [ $PYTHON_PROCS -gt 0 ]; then
        echo -e "${GREEN}✓ 发现 $PYTHON_PROCS 个Python后端进程${NC}"
        pgrep -f "python.*backend" | xargs ps -p | tail -n +2
    else
        echo -e "${YELLOW}⚠ 未发现Python后端进程${NC}"
    fi
    
    # 检查端口占用
    echo ""
    echo "端口占用情况:"
    for port in 8000 3000 8888; do
        if netstat -tlnp 2>/dev/null | grep ":$port " > /dev/null; then
            PROCESS=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | head -1)
            echo -e "  ${GREEN}✓ 端口 $port: $PROCESS${NC}"
        else
            echo -e "  ${YELLOW}⚠ 端口 $port: 未使用${NC}"
        fi
    done
    echo ""
}

# 检查系统资源
check_system_resources() {
    echo -e "${BLUE}💻 系统资源${NC}"
    echo "----------------------------------------"
    
    # CPU使用率
    if command -v top &> /dev/null; then
        CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
        echo "CPU使用率: $CPU_USAGE%"
    fi
    
    # 内存使用
    if command -v free &> /dev/null; then
        free -h | grep -E "^Mem|^Swap" | while read line; do
            echo "$line"
        done
    fi
    
    # 磁盘使用
    echo ""
    echo "磁盘使用情况:"
    df -h . | tail -n +2
    
    # GPU状态（如果有）
    if command -v nvidia-smi &> /dev/null; then
        echo ""
        echo "GPU状态:"
        nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits
    fi
    echo ""
}

# 检查网络连接
check_network() {
    echo -e "${BLUE}🌐 网络状态${NC}"
    echo "----------------------------------------"
    
    # 检查对外网络
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo -e "${GREEN}✓ 外网连接正常${NC}"
    else
        echo -e "${RED}✗ 外网连接异常${NC}"
    fi
    
    # 检查服务端口响应
    for port in 8000 3000; do
        if curl -s --connect-timeout 3 http://localhost:$port > /dev/null; then
            echo -e "${GREEN}✓ 端口 $port 响应正常${NC}"
        else
            echo -e "${YELLOW}⚠ 端口 $port 无响应${NC}"
        fi
    done
    echo ""
}

# 检查日志
check_logs() {
    echo -e "${BLUE}📄 日志状态${NC}"
    echo "----------------------------------------"
    
    # 检查日志文件
    if [ -f "logs/service.log" ]; then
        LOG_SIZE=$(du -h logs/service.log | cut -f1)
        LOG_LINES=$(wc -l < logs/service.log)
        echo -e "${GREEN}✓ 服务日志: $LOG_SIZE ($LOG_LINES 行)${NC}"
        
        # 显示最近的错误
        ERROR_COUNT=$(grep -i "error\|exception\|failed" logs/service.log | tail -10 | wc -l)
        if [ $ERROR_COUNT -gt 0 ]; then
            echo -e "${YELLOW}⚠ 发现 $ERROR_COUNT 条最近错误${NC}"
            echo "最新错误:"
            grep -i "error\|exception\|failed" logs/service.log | tail -3 | sed 's/^/  /'
        fi
    else
        echo -e "${YELLOW}⚠ 服务日志文件不存在${NC}"
    fi
    
    # 检查训练日志
    if [ -f "results/training_history.json" ]; then
        echo -e "${GREEN}✓ 训练历史文件存在${NC}"
    else
        echo -e "${YELLOW}⚠ 训练历史文件不存在${NC}"
    fi
    echo ""
}

# 检查数据和模型
check_data_models() {
    echo -e "${BLUE}📊 数据和模型${NC}"
    echo "----------------------------------------"
    
    # 检查数据文件
    if [ -d "data" ]; then
        echo "数据文件:"
        for file in weather.csv electricity.csv; do
            if [ -f "data/$file" ]; then
                SIZE=$(du -h "data/$file" | cut -f1)
                echo -e "  ${GREEN}✓ $file: $SIZE${NC}"
            else
                echo -e "  ${YELLOW}⚠ $file: 不存在${NC}"
            fi
        done
    fi
    
    # 检查模型文件
    if [ -d "models" ]; then
        MODEL_COUNT=$(find models -name "*.pth" -o -name "*.pkl" | wc -l)
        if [ $MODEL_COUNT -gt 0 ]; then
            echo -e "${GREEN}✓ 发现 $MODEL_COUNT 个模型文件${NC}"
            find models -name "*.pth" -o -name "*.pkl" | head -5 | while read model; do
                SIZE=$(du -h "$model" | cut -f1)
                echo "  $(basename "$model"): $SIZE"
            done
        else
            echo -e "${YELLOW}⚠ 未发现模型文件${NC}"
        fi
    fi
    
    # 检查结果文件
    if [ -d "results" ]; then
        RESULT_COUNT=$(find results -name "*.png" -o -name "*.json" | wc -l)
        if [ $RESULT_COUNT -gt 0 ]; then
            echo -e "${GREEN}✓ 发现 $RESULT_COUNT 个结果文件${NC}"
        else
            echo -e "${YELLOW}⚠ 未发现结果文件${NC}"
        fi
    fi
    echo ""
}

# 显示快速操作
show_quick_actions() {
    echo -e "${BLUE}🔧 快速操作${NC}"
    echo "----------------------------------------"
    echo "1. 查看实时日志: tail -f logs/service.log"
    echo "2. 重启服务: ./stop_service.sh && ./start_service.sh"
    echo "3. 进入tmux会话: tmux attach -t timevis"
    echo "4. 检查环境: ./check_environment.sh"
    echo "5. 查看API文档: curl http://localhost:8000/docs"
    echo "6. 监控GPU: watch -n 1 nvidia-smi"
    echo ""
}

# 实时监控模式
real_time_monitor() {
    echo -e "${CYAN}启动实时监控模式 (按 Ctrl+C 退出)${NC}"
    echo ""
    
    while true; do
        clear
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}      TimeVis 实时监控 $(date '+%H:%M:%S')      ${NC}"
        echo -e "${BLUE}========================================${NC}"
        echo ""
        
        # 简化的状态检查
        echo -e "${CYAN}服务状态:${NC}"
        if tmux has-session -t timevis 2>/dev/null; then
            echo -e "  ${GREEN}✓ tmux会话运行中${NC}"
        else
            echo -e "  ${YELLOW}⚠ tmux会话未运行${NC}"
        fi
        
        PYTHON_PROCS=$(pgrep -f "python.*backend" | wc -l)
        echo "  Python进程: $PYTHON_PROCS"
        
        # 资源使用
        echo -e "${CYAN}资源使用:${NC}"
        if command -v free &> /dev/null; then
            MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')
            echo "  内存使用: $MEM_USAGE"
        fi
        
        if command -v top &> /dev/null; then
            LOAD_AVG=$(uptime | awk -F'load average:' '{ print $2 }' | sed 's/^ *//')
            echo "  系统负载: $LOAD_AVG"
        fi
        
        # GPU状态
        if command -v nvidia-smi &> /dev/null; then
            GPU_USAGE=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1)
            echo "  GPU使用: ${GPU_USAGE}%"
        fi
        
        echo ""
        echo -e "${YELLOW}按 Ctrl+C 退出实时监控${NC}"
        
        sleep 5
    done
}

# 主函数
main() {
    case "${1:-status}" in
        "status")
            check_service_status
            check_system_resources
            check_network
            check_logs
            check_data_models
            show_quick_actions
            ;;
        "monitor")
            real_time_monitor
            ;;
        "logs")
            if [ -f "logs/service.log" ]; then
                echo -e "${BLUE}最新日志 (最后50行):${NC}"
                tail -50 logs/service.log
            else
                echo -e "${YELLOW}日志文件不存在${NC}"
            fi
            ;;
        "errors")
            if [ -f "logs/service.log" ]; then
                echo -e "${RED}错误日志:${NC}"
                grep -i "error\|exception\|failed" logs/service.log | tail -20
            else
                echo -e "${YELLOW}日志文件不存在${NC}"
            fi
            ;;
        *)
            echo "用法: $0 [status|monitor|logs|errors]"
            echo "  status  - 显示完整状态报告 (默认)"
            echo "  monitor - 实时监控模式"
            echo "  logs    - 显示最新日志"
            echo "  errors  - 显示错误日志"
            exit 1
            ;;
    esac
}

# 捕获Ctrl+C信号
trap 'echo -e "\n${YELLOW}监控已停止${NC}"; exit 0' INT

# 执行主函数
main "$@"
