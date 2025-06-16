# TimeVis 云端部署指南

## 📋 概述

本指南将帮助您在云服务器（阿里云、腾讯云、AWS、Google Cloud等）上部署TimeVis时间序列分析项目。

## 🚀 快速部署

### 方式一：一键部署脚本（推荐）

```bash
# 1. 克隆或上传项目到云服务器
git clone <your-repo> TimeVis
cd TimeVis

# 2. 赋予执行权限
chmod +x deploy_cloud.sh

# 3. 运行一键部署
./deploy_cloud.sh
```

### 方式二：Docker部署

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f
```

### 方式三：手动部署

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行数据处理
python data_processing.py

# 4. 训练模型
python model_training.py --model lstm
python model_training.py --model transformer

# 5. 启动服务
python -m backend.main
```

## 🖥️ 云服务器配置建议

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB
- **存储**: 20GB SSD
- **网络**: 1Mbps

### 推荐配置
- **CPU**: 4核心以上
- **内存**: 8GB以上
- **存储**: 50GB SSD
- **GPU**: NVIDIA GPU（可选，用于加速训练）

### GPU配置（可选）
- **NVIDIA GPU**: GTX 1060 或更高
- **显存**: 6GB以上
- **CUDA**: 11.8或更高版本

## 🌩️ 主要云平台部署指南

### 阿里云ECS

```bash
# 1. 创建ECS实例
# - 选择Ubuntu 20.04 LTS
# - 配置安全组开放端口：22, 8000, 3000

# 2. 连接服务器
ssh root@your-server-ip

# 3. 更新系统
apt update && apt upgrade -y

# 4. 安装Docker（可选）
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 5. 部署项目
git clone <your-repo> TimeVis
cd TimeVis
./deploy_cloud.sh
```

### 腾讯云CVM

```bash
# 1. 创建CVM实例
# - 选择Ubuntu Server 20.04 LTS
# - 配置安全组规则

# 2. 安装NVIDIA驱动（如果有GPU）
ubuntu-drivers autoinstall

# 3. 部署项目
wget -qO- https://your-repo/deploy_cloud.sh | bash
```

### AWS EC2

```bash
# 1. 启动EC2实例
# - AMI: Ubuntu Server 20.04 LTS
# - 实例类型: t3.medium或更高
# - 安全组: 开放22, 8000, 3000端口

# 2. 连接实例
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. 部署
sudo apt update
git clone <your-repo> TimeVis
cd TimeVis
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

## 🔧 环境配置

### 系统依赖

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv git curl htop

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl htop
```

### Python环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### GPU环境（可选）

```bash
# 安装NVIDIA驱动
sudo ubuntu-drivers autoinstall

# 安装CUDA Toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

# 安装cuDNN
# 从NVIDIA官网下载cuDNN并安装
```

## 📁 目录结构

```
TimeVis/
├── data/                   # 数据文件
│   ├── weather.csv
│   └── electricity.csv
├── models/                 # 训练后的模型
│   ├── lstm_model.pth
│   └── transformer_model.pth
├── results/               # 训练结果和可视化
│   ├── training_history.json
│   └── evaluation_plots.png
├── logs/                  # 日志文件
│   └── service.log
├── backend/               # 后端服务
├── frontend/              # 前端界面
├── data_processing.py     # 数据处理脚本
├── model_training.py      # 模型训练脚本
├── requirements.txt       # Python依赖
├── deploy_cloud.sh       # 云端部署脚本
├── docker-compose.yml    # Docker配置
└── Dockerfile           # Docker镜像配置
```

## 🔌 端口配置

| 服务 | 端口 | 说明 |
|------|------|------|
| Web界面 | 3000 | React前端界面 |
| API服务 | 8000 | FastAPI后端服务 |
| Jupyter | 8888 | Jupyter Lab（可选） |

### 安全组配置

确保在云服务器安全组中开放以下端口：
- 22 (SSH)
- 8000 (API)
- 3000 (Web)
- 8888 (Jupyter，可选)

## 🎯 运行和管理

### 启动服务

```bash
# 方式1：使用部署脚本
./deploy_cloud.sh start

# 方式2：手动启动
source venv/bin/activate
python -m backend.main

# 方式3：后台运行
nohup python -m backend.main > logs/service.log 2>&1 &
```

### 停止服务

```bash
# 停止tmux会话
tmux kill-session -t timevis

# 或者停止后台进程
./deploy_cloud.sh stop
```

### 查看状态

```bash
# 查看服务状态
tmux attach -t timevis

# 查看日志
tail -f logs/service.log

# 查看GPU使用情况
nvidia-smi

# 查看系统资源
htop
```

## 📊 性能监控

### 系统监控

```bash
# 实时监控
htop

# 磁盘使用
df -h

# 内存使用
free -h

# GPU监控
watch -n 1 nvidia-smi
```

### 服务监控

```bash
# 检查端口
netstat -tlnp | grep :8000

# 查看进程
ps aux | grep python

# 查看服务日志
tail -f logs/service.log
```

## 🔧 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Python依赖问题**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **GPU不可用**
   ```bash
   nvidia-smi
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

4. **内存不足**
   ```bash
   # 减少batch_size
   python model_training.py --batch_size 16
   
   # 启用交换空间
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### 日志分析

```bash
# 查看错误日志
grep -i error logs/service.log

# 查看最近日志
tail -n 100 logs/service.log

# 实时监控日志
tail -f logs/service.log | grep -i "error\|warning"
```

## 🔄 更新和维护

### 代码更新

```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖
pip install -r requirements.txt

# 重启服务
./deploy_cloud.sh stop
./deploy_cloud.sh start
```

### 数据备份

```bash
# 备份模型和结果
tar -czf backup_$(date +%Y%m%d).tar.gz models/ results/ data/

# 定时备份（添加到crontab）
0 2 * * * cd /path/to/TimeVis && tar -czf backup_$(date +\%Y\%m\%d).tar.gz models/ results/
```

## 📧 支持和联系

如果在部署过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目的Issue页面
3. 查看详细的运行日志
4. 提供完整的错误信息和环境配置

---

## 🎉 部署成功

部署成功后，您可以：

- 访问 `http://your-server-ip:3000` 查看Web界面
- 访问 `http://your-server-ip:8000/docs` 查看API文档
- 使用 `tmux attach -t timevis` 查看服务运行状态

祝您使用愉快！🚀
