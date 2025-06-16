"""
环境检查和安装脚本
检查并安装TimeVis所需的所有依赖
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def print_header():
    """打印标题"""
    print("=" * 60)
    print("TimeVis 环境检查和安装工具")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本 {version.major}.{version.minor} 不支持")
        print("请安装Python 3.8或更高版本")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """检查pip是否可用"""
    print("\n📦 检查pip...")
    try:
        import pip
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print("❌ pip不可用")
            return False
    except ImportError:
        print("❌ pip未安装")
        return False

def install_requirements():
    """安装requirements.txt中的依赖"""
    print("\n📥 安装依赖包...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return False
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            return True
        else:
            print(f"❌ 依赖安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程出错: {str(e)}")
        return False

def check_core_packages():
    """检查核心包是否正确安装"""
    print("\n🔍 检查核心包...")
    
    core_packages = {
        'torch': 'PyTorch',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'sklearn': 'Scikit-learn',
        'matplotlib': 'Matplotlib',
        'seaborn': 'Seaborn',
        'transformers': 'Transformers',
        'flask': 'Flask'
    }
    
    all_good = True
    
    for package, name in core_packages.items():
        try:
            if package == 'sklearn':
                importlib.import_module('sklearn')
            else:
                importlib.import_module(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} (未安装)")
            all_good = False
    
    return all_good

def check_gpu_support():
    """检查GPU支持"""
    print("\n🎮 检查GPU支持...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA可用 - {gpu_count}个GPU")
            print(f"   主GPU: {gpu_name}")
            return True
        else:
            print("⚠️  CUDA不可用，将使用CPU训练")
            return False
    except ImportError:
        print("❌ PyTorch未安装，无法检查GPU")
        return False

def check_data_files():
    """检查数据文件"""
    print("\n📁 检查数据文件...")
    
    data_dir = Path("data")
    required_files = ["weather.csv", "electricity.csv"]
    
    if not data_dir.exists():
        print("❌ data目录不存在")
        return False
    
    all_exist = True
    for file_name in required_files:
        file_path = data_dir / file_name
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ {file_name} ({size_mb:.1f}MB)")
        else:
            print(f"  ❌ {file_name} (不存在)")
            all_exist = False
    
    return all_exist

def create_directories():
    """创建必要的目录"""
    print("\n📂 创建目录结构...")
    
    directories = [
        "data/processed",
        "models",
        "results",
        "logs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")

def generate_config_file():
    """生成配置文件"""
    print("\n⚙️  生成配置文件...")
    
    config_content = """# TimeVis 配置文件
# 数据处理配置
DATA_DIR = "data"
PROCESSED_DIR = "data/processed"
MODELS_DIR = "models"
RESULTS_DIR = "results"

# 模型训练配置
BATCH_SIZE = 32
SEQUENCE_LENGTH = 60
HIDDEN_SIZE = 128
NUM_LAYERS = 2
DROPOUT = 0.2
LEARNING_RATE = 0.001
EPOCHS = 50

# GPU配置
USE_CUDA = True
DEVICE = "auto"  # auto, cpu, cuda

# Web应用配置
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
DEBUG = True

# 数据库配置
DATABASE_URL = "sqlite:///timevis.db"

# Redis配置（用于Celery）
REDIS_URL = "redis://localhost:6379/0"
"""
    
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("  ✅ config.py")

def run_quick_test():
    """运行快速测试"""
    print("\n🧪 运行快速测试...")
    
    try:
        # 测试数据加载
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=100, freq='H'),
            'value': np.random.randn(100)
        })
        
        print("  ✅ 数据处理功能正常")
        
        # 测试PyTorch
        import torch
        x = torch.randn(10, 5)
        print("  ✅ PyTorch功能正常")
        
        # 测试绘图
        import matplotlib.pyplot as plt
        plt.ioff()  # 关闭交互模式
        print("  ✅ 绘图功能正常")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print_header()
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 检查pip
    if not check_pip():
        return False
    
    # 创建目录结构
    create_directories()
    
    # 生成配置文件
    generate_config_file()
    
    # 安装依赖
    if not install_requirements():
        print("\n❌ 环境安装失败")
        return False
    
    # 检查核心包
    if not check_core_packages():
        print("\n❌ 核心包检查失败")
        return False
    
    # 检查GPU支持
    check_gpu_support()
    
    # 检查数据文件
    if not check_data_files():
        print("\n⚠️  数据文件缺失，请确保weather.csv和electricity.csv在data目录下")
    
    # 运行快速测试
    if not run_quick_test():
        print("\n❌ 快速测试失败")
        return False
    
    # 总结
    print("\n" + "=" * 60)
    print("🎉 环境检查和安装完成！")
    print("=" * 60)
    print("\n✅ 系统已就绪，可以开始使用TimeVis")
    print("\n📋 下一步操作:")
    print("1. 运行 python quick_start.py 开始完整流程")
    print("2. 或者运行 start_timevis.bat 使用图形化界面")
    print("3. 查看 QUICK_START.md 了解详细使用方法")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 安装过程中出现错误，请检查上述输出")
        sys.exit(1)
