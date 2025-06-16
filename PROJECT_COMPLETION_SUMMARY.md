# TimeVis 云端部署完成摘要

## 📋 项目概述

TimeVis 是一个基于 LSTM 和 Transformer 的时间序列预测与可视化系统，现已完成云服务器部署的全面配置。

## 🎯 已完成的核心功能

### 1. 数据处理系统
- **自动化数据清洗**: `data_processing.py`
- **特征工程**: 自动特征选择和异常值处理
- **数据可视化**: 生成数据分析报告
- **支持数据集**: weather.csv (气象数据) 和 electricity.csv (用电量数据)

### 2. 模型训练系统
- **LSTM模型**: 传统深度学习时间序列预测
- **Transformer模型**: 基于注意力机制的高级预测
- **自动化训练**: `model_training.py` 支持参数配置
- **结果评估**: 多种评估指标和可视化

### 3. 云端部署方案
- **一键部署脚本**: `deploy_cloud.sh`
- **Docker容器化**: `docker-compose.yml` 和 `Dockerfile`
- **环境检查工具**: `check_environment.sh/bat`
- **服务管理**: 启动/停止/监控脚本

## 🚀 部署选项

### 方式一：一键部署（推荐）
```bash
git clone <your-repo> TimeVis
cd TimeVis
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

### 方式二：Docker部署
```bash
docker-compose up -d
```

### 方式三：手动部署
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python data_processing.py
python model_training.py
```

## 📁 项目文件结构

```
TimeVis/
├── 📊 数据处理
│   ├── data_processing.py          # 数据清洗和预处理
│   ├── data/                       # 数据文件目录
│   │   ├── weather.csv            # 气象数据
│   │   └── electricity.csv        # 用电量数据
│   └── results/                   # 处理结果
│
├── 🤖 模型训练
│   ├── model_training.py          # 模型训练脚本
│   ├── models/                    # 训练后的模型
│   └── results/                  # 训练结果和可视化
│
├── 🌩️ 云端部署
│   ├── deploy_cloud.sh           # 一键部署脚本
│   ├── docker-compose.yml        # Docker配置
│   ├── Dockerfile                # 容器镜像配置
│   ├── requirements.txt          # Python依赖
│   └── CLOUD_DEPLOYMENT_GUIDE.md # 详细部署文档
│
├── 🔧 环境管理
│   ├── check_environment.sh/bat  # 环境检查工具
│   ├── install_dependencies.bat  # Windows依赖安装
│   ├── start_service.sh          # 服务启动脚本
│   ├── stop_service.sh           # 服务停止脚本
│   └── monitor_system.sh         # 系统监控工具
│
├── 🌐 服务后端
│   ├── backend/                  # FastAPI/Flask后端
│   ├── frontend/                 # Vue.js前端
│   └── logs/                     # 日志文件
│
└── 📖 文档
    ├── README.md                 # 项目主文档
    ├── DATA_PROCESSING_GUIDE.md  # 数据处理指南
    ├── CLOUD_DEPLOYMENT_GUIDE.md # 云端部署指南
    └── API_DOCS.md              # API文档
```

## 🎛️ 主要配置文件

### requirements.txt
- 包含所有必要的 Python 依赖
- 支持 CPU 和 GPU 环境
- 区分开发和生产环境依赖

### docker-compose.yml
- 完整的容器化配置
- 包含数据卷映射
- 支持服务编排

### deploy_cloud.sh
- 自动检测系统环境
- GPU/CPU 环境自适应
- 完整的部署流程

## 🔍 环境要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB
- **存储**: 20GB SSD
- **网络**: 1Mbps

### 推荐配置
- **CPU**: 4核心以上
- **内存**: 8GB以上
- **存储**: 50GB SSD
- **GPU**: NVIDIA GPU（可选）

### 支持的云平台
- ✅ 阿里云 ECS
- ✅ 腾讯云 CVM
- ✅ AWS EC2
- ✅ Google Cloud Compute
- ✅ Azure Virtual Machines

## 🚦 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Web界面 | 3000 | React/Vue.js 前端 |
| API服务 | 8000 | FastAPI 后端服务 |
| Jupyter | 8888 | Jupyter Lab（可选） |

## 🎮 使用流程

### 1. 环境准备
```bash
# 检查环境
./check_environment.sh

# 安装依赖（如需要）
./deploy_cloud.sh
```

### 2. 数据准备
- 将 `weather.csv` 和 `electricity.csv` 放入 `data/` 目录
- 运行数据处理：`python data_processing.py`

### 3. 模型训练
```bash
# 训练LSTM模型
python model_training.py --model lstm --epochs 50

# 训练Transformer模型
python model_training.py --model transformer --epochs 30
```

### 4. 启动服务
```bash
# 启动所有服务
./start_service.sh

# 查看服务状态
./monitor_system.sh
```

### 5. 访问系统
- Web界面: `http://your-server-ip:3000`
- API文档: `http://your-server-ip:8000/docs`

## 🔧 运维管理

### 常用命令
```bash
# 服务管理
./start_service.sh          # 启动服务
./stop_service.sh           # 停止服务
./monitor_system.sh         # 监控状态

# 日志查看
tail -f logs/service.log     # 实时日志
./monitor_system.sh logs    # 最新日志
./monitor_system.sh errors  # 错误日志

# 进程管理
tmux attach -t timevis      # 进入tmux会话
tmux kill-session -t timevis # 停止tmux会话
```

### 数据备份
```bash
# 备份重要数据
tar -czf backup_$(date +%Y%m%d).tar.gz models/ results/ data/

# 自动化备份（添加到crontab）
0 2 * * * cd /path/to/TimeVis && tar -czf backup_$(date +\%Y\%m\%d).tar.gz models/ results/
```

## 🚨 故障排除

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
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

4. **内存不足**
   ```bash
   # 减少batch_size
   python model_training.py --batch_size 16
   
   # 添加Swap
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## 📈 性能监控

### 系统监控
- 使用 `htop` 监控CPU和内存
- 使用 `nvidia-smi` 监控GPU
- 使用 `monitor_system.sh` 综合监控

### 服务监控
- 日志文件实时监控
- API健康检查
- 进程状态监控

## 🔄 更新维护

### 代码更新
```bash
git pull origin main
pip install -r requirements.txt
./stop_service.sh
./start_service.sh
```

### 依赖更新
```bash
pip install --upgrade -r requirements.txt
```

## 📞 技术支持

### 文档资源
- [完整部署指南](CLOUD_DEPLOYMENT_GUIDE.md)
- [数据处理文档](DATA_PROCESSING_GUIDE.md)
- [API接口文档](API_DOCS.md)

### 日志分析
- 服务日志: `logs/service.log`
- 训练日志: `results/training_history.json`
- 系统日志: `journalctl -u timevis`

## ✅ 部署检查清单

- [ ] 服务器环境配置完成
- [ ] Python虚拟环境创建
- [ ] 依赖包安装完成
- [ ] 数据文件上传完成
- [ ] 模型训练成功
- [ ] 服务启动正常
- [ ] 端口访问正常
- [ ] 监控系统配置
- [ ] 备份策略设置

## 🎉 部署成功

恭喜！TimeVis 时间序列预测系统已成功部署到云服务器。

您现在可以：
- 通过Web界面管理数据和模型
- 使用API接口进行预测
- 监控系统运行状态
- 扩展功能和算法

祝您使用愉快！🚀

---

**项目维护**: 定期更新依赖、备份数据、监控性能
**安全建议**: 配置防火墙、使用HTTPS、定期更新系统
**性能优化**: 根据使用情况调整资源配置和参数设置
