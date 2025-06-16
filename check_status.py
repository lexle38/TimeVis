"""
TimeVis 项目状态检查工具
检查项目完整性、数据状态、模型状态和运行环境
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

def print_banner():
    """打印横幅"""
    print("=" * 80)
    print("TimeVis 项目状态检查")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def check_project_structure():
    """检查项目结构"""
    print("\n📁 项目结构检查")
    print("-" * 40)
    
    required_files = [
        "data_processing.py",
        "model_training.py", 
        "quick_start.py",
        "setup_environment.py",
        "requirements.txt",
        "QUICK_START.md",
        "DATA_PROCESSING_GUIDE.md"
    ]
    
    required_dirs = [
        "data",
        "backend", 
        "frontend",
        "models",
        "results"
    ]
    
    # 检查文件
    missing_files = []
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name}")
            missing_files.append(file_name)
    
    # 检查目录
    missing_dirs = []
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/")
            missing_dirs.append(dir_name)
    
    return len(missing_files) == 0 and len(missing_dirs) == 0

def check_data_status():
    """检查数据状态"""
    print("\n📊 数据状态检查")
    print("-" * 40)
    
    data_dir = Path("data")
    processed_dir = data_dir / "processed"
    
    # 检查原始数据
    print("原始数据:")
    raw_files = ["weather.csv", "electricity.csv"]
    raw_data_ok = True
    
    for file_name in raw_files:
        file_path = data_dir / file_name
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ {file_name} ({size_mb:.1f}MB)")
        else:
            print(f"  ❌ {file_name} (缺失)")
            raw_data_ok = False
    
    # 检查处理后数据
    print("\n处理后数据:")
    if processed_dir.exists():
        processed_files = list(processed_dir.glob("*.csv"))
        if processed_files:
            for file_path in processed_files:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ {file_path.name} ({size_mb:.1f}MB)")
        else:
            print("  ⚠️  暂无处理后数据")
        
        # 检查数据集信息
        info_file = processed_dir / "datasets_info.json"
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                print(f"  ✅ datasets_info.json ({len(info)}个数据集)")
            except:
                print("  ❌ datasets_info.json (格式错误)")
        else:
            print("  ⚠️  datasets_info.json (未生成)")
    else:
        print("  ⚠️  processed目录不存在")
    
    return raw_data_ok

def check_model_status():
    """检查模型状态"""
    print("\n🤖 模型状态检查")
    print("-" * 40)
    
    models_dir = Path("models")
    
    if not models_dir.exists():
        print("  ⚠️  models目录不存在")
        return False
    
    model_files = list(models_dir.glob("*.pth"))
    
    if not model_files:
        print("  ⚠️  暂无训练好的模型")
        return False
    
    print("已训练模型:")
    for model_path in model_files:
        size_mb = model_path.stat().st_size / (1024 * 1024)
        mod_time = datetime.fromtimestamp(model_path.stat().st_mtime)
        print(f"  ✅ {model_path.name} ({size_mb:.1f}MB, {mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    return True

def check_results_status():
    """检查结果状态"""
    print("\n📈 结果状态检查")
    print("-" * 40)
    
    results_dir = Path("results")
    
    if not results_dir.exists():
        print("  ⚠️  results目录不存在")
        return False
    
    # 检查结果文件
    result_files = {
        "*.json": "训练结果",
        "*.csv": "数据报告", 
        "*.html": "可视化报告",
        "*.png": "图表文件"
    }
    
    has_results = False
    for pattern, desc in result_files.items():
        files = list(results_dir.glob(pattern))
        if files:
            print(f"\n{desc}:")
            for file_path in files:
                size_kb = file_path.stat().st_size / 1024
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                print(f"  ✅ {file_path.name} ({size_kb:.1f}KB, {mod_time.strftime('%Y-%m-%d %H:%M')})")
            has_results = True
    
    if not has_results:
        print("  ⚠️  暂无结果文件")
    
    return has_results

def check_environment():
    """检查运行环境"""
    print("\n🔧 环境状态检查")
    print("-" * 40)
    
    # Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python版本: {python_version}")
    
    # 关键包检查
    packages = {
        'torch': 'PyTorch',
        'pandas': 'Pandas', 
        'numpy': 'NumPy',
        'sklearn': 'Scikit-learn',
        'matplotlib': 'Matplotlib',
        'flask': 'Flask'
    }
    
    env_ok = True
    print("\n核心依赖:")
    for package, name in packages.items():
        try:
            if package == 'sklearn':
                import sklearn
                version = sklearn.__version__
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
            print(f"  ✅ {name} ({version})")
        except ImportError:
            print(f"  ❌ {name} (未安装)")
            env_ok = False
    
    # GPU检查
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"\nGPU: ✅ {gpu_name}")
        else:
            print(f"\nGPU: ⚠️  CUDA不可用")
    except:
        print(f"\nGPU: ❌ 无法检查")
    
    return env_ok

def check_web_components():
    """检查Web组件状态"""
    print("\n🌐 Web组件检查")
    print("-" * 40)
    
    # 后端检查
    backend_dir = Path("backend")
    if backend_dir.exists():
        backend_files = ["app.py", "models.py", "api.py"]
        print("后端组件:")
        for file_name in backend_files:
            file_path = backend_dir / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ⚠️  {file_name} (缺失)")
    else:
        print("❌ backend目录不存在")
    
    # 前端检查
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            print("前端组件:")
            print("  ✅ package.json")
            
            node_modules = frontend_dir / "node_modules"
            if node_modules.exists():
                print("  ✅ node_modules (已安装依赖)")
            else:
                print("  ⚠️  node_modules (需要运行 npm install)")
        else:
            print("❌ 前端package.json不存在")
    else:
        print("❌ frontend目录不存在")

def generate_status_report():
    """生成状态报告"""
    print("\n📋 生成状态报告")
    print("-" * 40)
    
    report = {
        "检查时间": datetime.now().isoformat(),
        "项目状态": "完整" if check_project_structure() else "不完整",
        "数据状态": "可用" if check_data_status() else "缺失",
        "模型状态": "已训练" if check_model_status() else "未训练", 
        "环境状态": "正常" if check_environment() else "异常"
    }
    
    # 保存报告
    with open("PROJECT_STATUS.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 状态报告已保存: PROJECT_STATUS.json")

def provide_recommendations():
    """提供建议"""
    print("\n💡 操作建议")
    print("-" * 40)
    
    # 检查各个状态并给出建议
    if not Path("data/weather.csv").exists() or not Path("data/electricity.csv").exists():
        print("❗ 数据文件缺失:")
        print("   请确保 weather.csv 和 electricity.csv 在 data/ 目录下")
    
    if not Path("data/processed").exists() or not list(Path("data/processed").glob("*.csv")):
        print("❗ 需要数据处理:")
        print("   运行: python data_processing.py")
        print("   或: python quick_start.py --data-only")
    
    if not Path("models").exists() or not list(Path("models").glob("*.pth")):
        print("❗ 需要模型训练:")
        print("   运行: python model_training.py") 
        print("   或: python quick_start.py --model-only")
    
    if not Path("results").exists() or not list(Path("results").glob("*")):
        print("❗ 需要生成结果:")
        print("   运行完整流程: python quick_start.py")
    
    print("\n🚀 快速启动:")
    print("   一键运行: start_timevis.bat")
    print("   或: python quick_start.py")

def main():
    """主函数"""
    print_banner()
    
    # 执行各项检查
    check_project_structure()
    check_data_status()
    check_model_status()
    check_results_status()
    check_environment()
    check_web_components()
    
    # 生成报告和建议
    generate_status_report()
    provide_recommendations()
    
    print("\n" + "=" * 80)
    print("状态检查完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
