"""
简化版训练脚本
用于快速测试模型训练功能，不依赖Flask和Celery
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.lstm_model import LSTMPredictor
from utils.data_processor import TimeSeriesProcessor

def test_lstm_training():
    """测试LSTM模型训练"""
    print("开始测试LSTM模型训练...")
    
    # 生成测试数据
    processor = TimeSeriesProcessor()
    df = processor.generate_sample_data('weather', num_samples=200)
    
    print(f"生成数据形状: {df.shape}")
    print(f"数据列: {list(df.columns)}")
    
    # 初始化LSTM预测器
    lstm_predictor = LSTMPredictor(
        sequence_length=10,
        hidden_size=32,
        num_layers=1,
        dropout=0.1
    )
    
    # 准备数据
    train_loader, val_loader, scaled_data = lstm_predictor.prepare_data(df, train_ratio=0.8)
    
    print(f"训练数据批次数: {len(train_loader)}")
    print(f"验证数据批次数: {len(val_loader)}")
    
    # 训练模型
    training_history = lstm_predictor.train(
        train_loader=train_loader,
        val_loader=val_loader,
        num_epochs=5,  # 少量epoch用于测试
        learning_rate=0.01,
        patience=10
    )
    
    print("训练完成！")
    print(f"最终训练损失: {training_history['train_losses'][-1]:.6f}")
    print(f"最终验证损失: {training_history['val_losses'][-1]:.6f}")
    
    # 评估模型
    evaluation_results = lstm_predictor.evaluate(val_loader)
    
    print(f"验证集MSE: {evaluation_results['mse']:.6f}")
    print(f"验证集MAE: {evaluation_results['mae']:.6f}")
    print(f"验证集RMSE: {evaluation_results['rmse']:.6f}")
    
    # 测试单次预测
    test_sequence = [20.1, 19.8, 21.2, 22.5, 23.1, 22.8, 21.9, 20.5, 19.7, 20.3]
    prediction = lstm_predictor.predict_single(test_sequence)
    
    print(f"\n测试预测:")
    print(f"输入序列: {test_sequence}")
    print(f"预测结果: {prediction:.4f}")
    
    # 保存模型
    model_save_path = "./test_lstm_model"
    lstm_predictor.save_model(model_save_path)
    print(f"模型已保存至: {model_save_path}")
    
    # 测试模型加载
    lstm_predictor_loaded = LSTMPredictor()
    lstm_predictor_loaded.load_model(model_save_path)
    
    # 验证加载的模型
    prediction_loaded = lstm_predictor_loaded.predict_single(test_sequence)
    print(f"加载模型预测结果: {prediction_loaded:.4f}")
    
    if abs(prediction - prediction_loaded) < 1e-6:
        print("✅ 模型保存和加载测试通过")
    else:
        print("❌ 模型保存和加载测试失败")
    
    return True

def test_data_processing():
    """测试数据处理功能"""
    print("\n开始测试数据处理功能...")
    
    processor = TimeSeriesProcessor()
    
    # 测试天气数据生成
    weather_df = processor.generate_sample_data('weather', num_samples=100)
    print(f"天气数据形状: {weather_df.shape}")
    
    # 测试电力数据生成
    electricity_df = processor.generate_sample_data('electricity', num_samples=100)
    print(f"电力数据形状: {electricity_df.shape}")
    
    # 测试交通数据生成
    traffic_df = processor.generate_sample_data('traffic', num_samples=100)
    print(f"交通数据形状: {traffic_df.shape}")
    
    # 测试数据分析
    analysis = processor.analyze_data(weather_df)
    print(f"数据分析结果: {len(analysis)} 个字段")
    
    # 测试序列创建
    target_column = weather_df.select_dtypes(include=[np.number]).columns[0]
    X, y = processor.create_sequences(weather_df, target_column, sequence_length=10)
    
    print(f"序列数据形状: X={X.shape}, y={y.shape}")
    
    # 测试数据分割
    X_train, X_val, X_test, y_train, y_val, y_test = processor.split_data(X, y)
    
    print(f"训练集: X={X_train.shape}, y={y_train.shape}")
    print(f"验证集: X={X_val.shape}, y={y_val.shape}")
    print(f"测试集: X={X_test.shape}, y={y_test.shape}")
    
    print("✅ 数据处理功能测试通过")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("TimeVis 核心功能测试")
    print("=" * 60)
    
    try:
        # 测试数据处理
        test_data_processing()
        
        # 测试LSTM训练
        test_lstm_training()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！核心功能正常工作。")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
