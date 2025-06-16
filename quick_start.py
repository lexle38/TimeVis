"""
TimeVis 一键启动脚本
自动执行数据处理、模型训练和结果分析的完整流程
"""

import os
import sys
import time
import subprocess
from datetime import datetime
import argparse

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                        TimeVis 一键启动                         ║
    ║                    时间序列预测系统自动化脚本                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查系统依赖...")
    
    required_packages = [
        'torch', 'pandas', 'numpy', 'sklearn', 
        'matplotlib', 'seaborn', 'transformers'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} (缺失)")
    
    if missing_packages:
        print(f"\n⚠️  缺失依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖检查通过")
    return True

def check_data_files():
    """检查数据文件"""
    print("\n📁 检查数据文件...")
    
    data_files = ['data/weather.csv', 'data/electricity.csv']
    all_exist = True
    
    for file_path in data_files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  ✅ {file_path} ({size_mb:.1f}MB)")
        else:
            print(f"  ❌ {file_path} (不存在)")
            all_exist = False
    
    if not all_exist:
        print("\n⚠️  请确保数据文件存在于 data/ 目录下")
        return False
    
    print("✅ 数据文件检查通过")
    return True

def run_data_processing():
    """运行数据处理"""
    print("\n" + "="*60)
    print("🔄 开始数据处理...")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # 导入并运行数据处理
        from data_processing import TimeSeriesDataProcessor
        
        processor = TimeSeriesDataProcessor()
        
        # 分析和处理天气数据
        processor.analyze_weather_data()
        weather_df = processor.process_weather_data()
        
        # 分析和处理用电量数据
        processor.analyze_electricity_data()
        electricity_df = processor.process_electricity_data()
        
        # 生成数据集信息
        processor.generate_datasets_info()
        
        # 生成可视化报告
        processor.generate_visualization_report()
        
        processing_time = time.time() - start_time
        print(f"\n✅ 数据处理完成 (耗时: {processing_time:.1f}秒)")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据处理失败: {str(e)}")
        return False

def run_model_training():
    """运行模型训练"""
    print("\n" + "="*60)
    print("🤖 开始模型训练...")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # 导入并运行模型训练
        from model_training import ModelFineTuner
        
        trainer = ModelFineTuner()
        
        # 加载数据集
        datasets = trainer.load_datasets()
        
        if not datasets:
            print("❌ 未找到可用数据集，请先运行数据处理")
            return False
        
        # 为每个数据集训练模型
        for dataset_info in datasets:
            print(f"\n📊 训练数据集: {dataset_info['name']}")
            
            # 加载数据
            data = trainer.load_data_for_training(dataset_info['name'])
            if data is None:
                continue
            
            # 准备数据
            X_train, X_test, y_train, y_test, scaler = trainer.prepare_data(data)
            
            # 训练LSTM模型
            print("🧠 训练LSTM模型...")
            lstm_model, lstm_history = trainer.train_lstm_model(
                X_train, y_train, X_test, y_test
            )
            
            # 训练Transformer模型
            print("🔄 训练Transformer模型...")
            transformer_model, transformer_history = trainer.train_transformer_model(
                X_train, y_train, X_test, y_test
            )
            
            # 评估和比较模型
            trainer.evaluate_and_compare_models(
                {'LSTM': lstm_model, 'Transformer': transformer_model},
                X_test, y_test, scaler, dataset_info['name']
            )
        
        # 生成综合报告
        trainer.generate_comprehensive_report()
        
        training_time = time.time() - start_time
        print(f"\n✅ 模型训练完成 (耗时: {training_time:.1f}秒)")
        return True
        
    except Exception as e:
        print(f"\n❌ 模型训练失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def generate_summary_report():
    """生成总结报告"""
    print("\n" + "="*60)
    print("📋 生成总结报告...")
    print("="*60)
    
    try:
        report_content = f"""
# TimeVis 执行总结报告

**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 数据处理结果
- ✅ 天气数据处理完成
- ✅ 用电量数据处理完成
- ✅ 数据集信息生成完成
- ✅ 可视化报告生成完成

## 🤖 模型训练结果
- ✅ LSTM模型训练完成
- ✅ Transformer模型训练完成
- ✅ 模型性能评估完成
- ✅ 模型对比报告生成完成

## 📁 生成的文件
### 数据文件
- `data/processed/weather_processed.csv` - 处理后的天气数据
- `data/processed/electricity_processed.csv` - 处理后的用电量数据
- `data/processed/datasets_info.json` - 数据集信息

### 模型文件
- `models/lstm_weather.pth` - 天气预测LSTM模型
- `models/transformer_weather.pth` - 天气预测Transformer模型
- `models/lstm_electricity.pth` - 用电量预测LSTM模型
- `models/transformer_electricity.pth` - 用电量预测Transformer模型

### 结果报告
- `results/weather_training_results.json` - 天气模型训练结果
- `results/electricity_training_results.json` - 用电量模型训练结果
- `results/comprehensive_report.html` - 综合分析报告
- `results/data_visualization_report.html` - 数据可视化报告

## 🚀 下一步操作
1. 查看结果报告: 打开 `results/comprehensive_report.html`
2. 启动Web应用: 运行 `python backend/app.py`
3. 使用API接口: 参考 `API_DOCS.md`

## 📖 详细文档
- 数据处理指南: `DATA_PROCESSING_GUIDE.md`
- 快速启动指南: `QUICK_START.md`
- API文档: `API_DOCS.md`
        """
        
        with open('EXECUTION_SUMMARY.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print("✅ 总结报告已生成: EXECUTION_SUMMARY.md")
        return True
        
    except Exception as e:
        print(f"❌ 生成报告失败: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TimeVis 一键启动脚本')
    parser.add_argument('--data-only', action='store_true', help='只执行数据处理')
    parser.add_argument('--model-only', action='store_true', help='只执行模型训练')
    parser.add_argument('--skip-checks', action='store_true', help='跳过依赖检查')
    
    args = parser.parse_args()
    
    print_banner()
    
    # 记录开始时间
    total_start_time = time.time()
    
    # 检查依赖和数据文件
    if not args.skip_checks:
        if not check_dependencies():
            sys.exit(1)
        
        if not check_data_files():
            sys.exit(1)
    
    success = True
    
    # 执行数据处理
    if not args.model_only:
        if not run_data_processing():
            success = False
    
    # 执行模型训练
    if not args.data_only and success:
        if not run_model_training():
            success = False
    
    # 生成总结报告
    if success:
        generate_summary_report()
        
        total_time = time.time() - total_start_time
        print(f"\n🎉 所有任务完成! 总耗时: {total_time:.1f}秒")
        print("\n📋 查看执行总结: EXECUTION_SUMMARY.md")
        print("🌐 启动Web应用: python backend/app.py")
        print("📚 查看详细文档: QUICK_START.md")
    else:
        print("\n❌ 执行过程中出现错误，请检查上述输出")
        sys.exit(1)

if __name__ == "__main__":
    main()
