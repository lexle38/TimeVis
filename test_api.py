"""
简单的系统测试脚本
用于验证后端API功能
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:5000/api"

def test_health():
    """测试健康检查接口"""
    print("测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print("❌ 健康检查失败")
            print(f"状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

def test_sample_data():
    """测试示例数据生成"""
    print("\n测试示例数据生成...")
    try:
        data = {
            "data_type": "weather",
            "num_samples": 100
        }
        response = requests.post(f"{BASE_URL}/sample-data", json=data)
        if response.status_code == 200:
            print("✅ 示例数据生成成功")
            result = response.json()
            dataset_id = result['dataset_id']
            print(f"数据集ID: {dataset_id}")
            return dataset_id
        else:
            print("❌ 示例数据生成失败")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 示例数据生成异常: {e}")
    return None

def test_datasets(dataset_id=None):
    """测试数据集接口"""
    print("\n测试数据集接口...")
    try:
        # 获取数据集列表
        response = requests.get(f"{BASE_URL}/datasets")
        if response.status_code == 200:
            print("✅ 获取数据集列表成功")
            datasets = response.json()['datasets']
            print(f"数据集数量: {len(datasets)}")
            
            # 如果有数据集，测试获取详情
            if dataset_id or datasets:
                test_id = dataset_id or datasets[0]['id']
                response = requests.get(f"{BASE_URL}/datasets/{test_id}")
                if response.status_code == 200:
                    print("✅ 获取数据集详情成功")
                    dataset_info = response.json()
                    print(f"数据集形状: {dataset_info['shape']}")
                else:
                    print("❌ 获取数据集详情失败")
        else:
            print("❌ 获取数据集列表失败")
    except Exception as e:
        print(f"❌ 数据集接口测试异常: {e}")

def test_training(dataset_id):
    """测试训练接口"""
    print("\n测试训练接口...")
    if not dataset_id:
        print("❌ 没有可用的数据集ID")
        return None
    
    try:
        # 测试LSTM训练（比较快）
        train_config = {
            "dataset_id": dataset_id,
            "model_type": "lstm",
            "data_type": "weather",
            "model_config": {
                "sequence_length": 5,
                "hidden_size": 32,
                "num_layers": 1,
                "num_epochs": 3,
                "learning_rate": 0.01
            }
        }
        
        response = requests.post(f"{BASE_URL}/train", json=train_config)
        if response.status_code == 200:
            print("✅ 训练任务启动成功")
            result = response.json()
            task_id = result['task_id']
            print(f"任务ID: {task_id}")
            return task_id
        else:
            print("❌ 训练任务启动失败")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 训练接口测试异常: {e}")
    return None

def test_task_status(task_id):
    """测试任务状态查询"""
    print(f"\n监控任务状态 (任务ID: {task_id})...")
    if not task_id:
        print("❌ 没有可用的任务ID")
        return
    
    try:
        for i in range(10):  # 最多检查10次
            response = requests.get(f"{BASE_URL}/tasks/{task_id}")
            if response.status_code == 200:
                task_info = response.json()
                status = task_info['status']
                progress = task_info.get('progress', 0)
                print(f"任务状态: {status}, 进度: {progress:.1%}")
                
                if status == 'completed':
                    print("✅ 任务完成")
                    return task_info
                elif status == 'failed':
                    print("❌ 任务失败")
                    print(f"错误信息: {task_info.get('error_message')}")
                    return None
                elif status == 'running':
                    print("⏳ 任务运行中...")
                    time.sleep(5)  # 等待5秒
                else:
                    print(f"任务状态: {status}")
                    time.sleep(2)
            else:
                print("❌ 获取任务状态失败")
                break
        
        print("⚠️ 任务监控超时")
        
    except Exception as e:
        print(f"❌ 任务状态查询异常: {e}")

def test_models():
    """测试模型接口"""
    print("\n测试模型接口...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            print("✅ 获取模型列表成功")
            models = response.json()['models']
            print(f"模型数量: {len(models)}")
            
            if models:
                model_id = models[0]['id']
                response = requests.get(f"{BASE_URL}/models/{model_id}")
                if response.status_code == 200:
                    print("✅ 获取模型详情成功")
                    model_info = response.json()
                    print(f"模型类型: {model_info['model_type']}")
                    return model_id
                else:
                    print("❌ 获取模型详情失败")
        else:
            print("❌ 获取模型列表失败")
    except Exception as e:
        print(f"❌ 模型接口测试异常: {e}")
    return None

def test_prediction(model_id):
    """测试预测接口"""
    print("\n测试预测接口...")
    if not model_id:
        print("❌ 没有可用的模型ID")
        return
    
    try:
        predict_config = {
            "model_id": model_id,
            "input_sequence": [20.1, 19.8, 21.2, 22.5, 23.1]
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=predict_config)
        if response.status_code == 200:
            print("✅ 预测任务启动成功")
            result = response.json()
            task_id = result['task_id']
            
            # 等待预测完成
            time.sleep(3)
            response = requests.get(f"{BASE_URL}/tasks/{task_id}")
            if response.status_code == 200:
                task_info = response.json()
                if task_info['status'] == 'completed':
                    print("✅ 预测完成")
                    if 'task_results' in task_info:
                        prediction = task_info['task_results']['results']['prediction']
                        print(f"预测结果: {prediction}")
                else:
                    print(f"预测状态: {task_info['status']}")
        else:
            print("❌ 预测任务启动失败")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 预测接口测试异常: {e}")

def test_stats():
    """测试统计接口"""
    print("\n测试统计接口...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            print("✅ 获取统计信息成功")
            stats = response.json()
            print(f"总任务数: {stats['total_tasks']}")
            print(f"已完成任务数: {stats['completed_tasks']}")
            print(f"模型数量: {stats['total_models']}")
        else:
            print("❌ 获取统计信息失败")
    except Exception as e:
        print(f"❌ 统计接口测试异常: {e}")

def main():
    """主测试函数"""
    print("=" * 50)
    print("TimeVis 系统测试")
    print("=" * 50)
    
    # 测试健康检查
    test_health()
    
    # 生成示例数据
    dataset_id = test_sample_data()
    
    # 测试数据集接口
    test_datasets(dataset_id)
    
    # 测试训练接口
    task_id = test_training(dataset_id)
    
    # 监控任务状态
    if task_id:
        test_task_status(task_id)
    
    # 测试模型接口
    model_id = test_models()
    
    # 测试预测接口
    if model_id:
        test_prediction(model_id)
    
    # 测试统计接口
    test_stats()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
