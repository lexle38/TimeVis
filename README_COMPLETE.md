# TimeVis - 时间序列预测系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

TimeVis是一个完整的时间序列预测系统，支持LSTM和Transformer模型的微调训练，提供自动化数据处理、模型训练和Web可视化界面。

## 🚀 一键启动

### 方法一：图形化启动（推荐）
```bash
# Windows用户直接双击
start_timevis.bat

# 或在命令行中运行
.\start_timevis.bat
```

### 方法二：Python一键启动
```bash
# 首次运行 - 环境检查和安装
python setup_environment.py

# 一键执行完整流程
python quick_start.py

# 检查项目状态
python check_status.py
```

## 📋 系统要求

- **Python**: 3.8+
- **系统**: Windows/Linux/macOS  
- **内存**: 建议8GB+
- **存储**: 2GB可用空间
- **GPU**: 可选，支持CUDA加速

## 📊 数据集

### 1. 天气数据 (weather.csv)
- **大小**: 7MB，52,698条记录
- **频率**: 每10分钟
- **特征**: 温度、湿度、风速、降雨量、气压等
- **用途**: 天气预测模型训练

### 2. 用电量数据 (electricity.csv)  
- **大小**: 95MB，大规模时间序列
- **频率**: 每小时
- **特征**: 320个电力消耗指标
- **用途**: 用电量预测模型训练

## 🔧 功能特性

### 数据处理
- ✅ 自动数据清洗和预处理
- ✅ 异常值检测和处理
- ✅ 特征工程和选择
- ✅ 数据可视化报告生成

### 模型训练
- ✅ LSTM深度学习模型
- ✅ Transformer注意力模型
- ✅ 自动超参数优化
- ✅ 模型性能对比分析

### Web界面
- ✅ Flask后端API
- ✅ React前端界面
- ✅ 实时预测展示
- ✅ 交互式图表

## 📁 项目结构

```
TimeVis/
├── data/                     # 数据目录
│   ├── weather.csv          # 天气数据
│   ├── electricity.csv      # 用电量数据
│   └── processed/           # 处理后数据
├── backend/                 # 后端代码
│   ├── app.py              # Flask应用
│   ├── models.py           # 数据模型
│   └── api.py              # API接口
├── frontend/               # 前端代码
│   ├── src/                # React源码
│   └── package.json        # 依赖配置
├── models/                 # 训练模型
├── results/                # 结果报告
├── data_processing.py      # 数据处理脚本
├── model_training.py       # 模型训练脚本
├── quick_start.py          # 一键启动脚本
├── setup_environment.py    # 环境安装脚本
├── check_status.py         # 状态检查脚本
└── start_timevis.bat       # Windows启动脚本
```

## 📚 详细文档

- 📖 [快速启动指南](QUICK_START.md) - 详细的启动步骤
- 🔧 [数据处理指南](DATA_PROCESSING_GUIDE.md) - 数据处理详细说明
- 🌐 [API接口文档](API_DOCS.md) - Web API使用说明
- 📊 [执行总结报告](EXECUTION_SUMMARY.md) - 自动生成的运行报告

## ⚡ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd TimeVis
```

### 2. 检查环境
```bash
python setup_environment.py
```

### 3. 一键运行
```bash
# Windows用户
start_timevis.bat

# 其他系统
python quick_start.py
```

### 4. 查看结果
- 训练报告: `results/comprehensive_report.html`
- 数据分析: `results/data_visualization_report.html`
- 执行总结: `EXECUTION_SUMMARY.md`

## 🌐 Web应用

### 启动后端
```bash
# 启动Redis (Windows)
redis-server

# 启动Celery Worker
python backend/celery_worker.py

# 启动Flask应用
python backend/app.py
```

### 启动前端
```bash
cd frontend
npm install
npm run dev
```

### 访问地址
- **前端**: http://localhost:3000
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/docs

## 🔍 常见问题

### Q: 依赖安装失败？
```bash
# 升级pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

### Q: CUDA不可用？
系统会自动切换到CPU模式，训练时间会相应增加。

### Q: 数据文件缺失？
确保`weather.csv`和`electricity.csv`在`data/`目录下。

### Q: 内存不足？
可以在配置文件中调整批处理大小：
```python
BATCH_SIZE = 16  # 默认32，可调整为更小值
```

## 📈 性能指标

### 模型性能（示例）
| 模型 | 数据集 | MSE | MAE | R² |
|------|--------|-----|-----|-----|
| LSTM | 天气数据 | 0.015 | 0.098 | 0.92 |
| Transformer | 天气数据 | 0.012 | 0.089 | 0.94 |
| LSTM | 用电量数据 | 0.023 | 0.121 | 0.89 |
| Transformer | 用电量数据 | 0.019 | 0.108 | 0.91 |

### 系统性能
- **数据处理**: ~30秒 (天气) + ~2分钟 (用电量)
- **模型训练**: ~5分钟 (GPU) / ~20分钟 (CPU)
- **预测延迟**: <100ms (单次预测)

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目主页**: [GitHub Repository]
- **问题反馈**: [Issues]
- **邮箱**: your-email@example.com

## 🙏 致谢

- [PyTorch](https://pytorch.org/) - 深度学习框架
- [Transformers](https://huggingface.co/transformers/) - 预训练模型库
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [React](https://reactjs.org/) - 前端框架

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！
