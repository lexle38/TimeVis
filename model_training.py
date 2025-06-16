"""
模型微调脚本
支持LSTM和Qwen模型的微调训练
"""

import os
import json
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ModelFineTuner:
    def __init__(self, data_dir='data/processed'):
        self.data_dir = data_dir
        self.models_dir = 'models'
        self.results_dir = 'results'
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        
        # 检查GPU可用性
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
    def load_datasets(self):
        """加载处理后的数据集"""
        datasets_info_path = os.path.join(self.data_dir, 'datasets_info.json')
        
        if not os.path.exists(datasets_info_path):
            print("未找到数据集信息文件，请先运行 data_processing.py")
            return []
        
        with open(datasets_info_path, 'r', encoding='utf-8') as f:
            datasets_info = json.load(f)
        
        available_datasets = []
        for info in datasets_info:
            dataset_path = os.path.join(self.data_dir, f"{info['name']}.csv")
            if os.path.exists(dataset_path):
                available_datasets.append(info)
                print(f"发现数据集: {info['name']} - {info['description']}")
            else:
                print(f"数据集文件不存在: {dataset_path}")
        
        return available_datasets
    
    def prepare_lstm_data(self, data, sequence_length=60, test_size=0.2):
        """准备LSTM训练数据"""
        print(f"准备LSTM数据，序列长度: {sequence_length}")
        
        # 数据归一化
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))
        
        # 创建序列数据
        X, y = [], []
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        
        # 分割训练和测试集
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # 转换为PyTorch张量
        X_train = torch.FloatTensor(X_train).unsqueeze(-1).to(self.device)
        y_train = torch.FloatTensor(y_train).to(self.device)
        X_test = torch.FloatTensor(X_test).unsqueeze(-1).to(self.device)
        y_test = torch.FloatTensor(y_test).to(self.device)
        
        return X_train, y_train, X_test, y_test, scaler
    
    def create_lstm_model(self, input_size=1, hidden_size=128, num_layers=2, output_size=1):
        """创建LSTM模型"""
        class LSTMModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers, output_size):
                super(LSTMModel, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                                  batch_first=True, dropout=0.2)
                self.dropout = nn.Dropout(0.2)
                self.fc = nn.Linear(hidden_size, output_size)
                
            def forward(self, x):
                # 初始化隐藏状态
                h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                
                # LSTM前向传播
                out, _ = self.lstm(x, (h0, c0))
                out = self.dropout(out[:, -1, :])  # 取最后一个时间步
                out = self.fc(out)
                return out
        
        return LSTMModel(input_size, hidden_size, num_layers, output_size).to(self.device)
    
    def train_lstm_model(self, dataset_name, hyperparameters=None):
        """训练LSTM模型"""
        print(f"\\n{'='*60}")
        print(f"开始训练LSTM模型 - {dataset_name}")
        print(f"{'='*60}")
        
        # 默认超参数
        default_params = {
            'sequence_length': 60,
            'hidden_size': 128,
            'num_layers': 2,
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 100,
            'test_size': 0.2
        }
        
        if hyperparameters:
            default_params.update(hyperparameters)
        
        params = default_params
        print(f"使用超参数: {params}")
        
        # 加载数据
        dataset_path = os.path.join(self.data_dir, f"{dataset_name}.csv")
        df = pd.read_csv(dataset_path)
        
        # 确保有value列
        if 'value' in df.columns:
            data = df['value']
        else:
            # 使用第一个数值列
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            data = df[numeric_cols[0]]
        
        print(f"数据形状: {data.shape}")
        print(f"数据范围: {data.min():.4f} - {data.max():.4f}")
        
        # 准备数据
        X_train, y_train, X_test, y_test, scaler = self.prepare_lstm_data(
            data, params['sequence_length'], params['test_size']
        )
        
        print(f"训练集形状: X_train: {X_train.shape}, y_train: {y_train.shape}")
        print(f"测试集形状: X_test: {X_test.shape}, y_test: {y_test.shape}")
        
        # 创建模型
        model = self.create_lstm_model(
            input_size=1,
            hidden_size=params['hidden_size'],
            num_layers=params['num_layers'],
            output_size=1
        )
        
        print(f"模型参数数量: {sum(p.numel() for p in model.parameters()):,}")
        
        # 定义损失函数和优化器
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=params['learning_rate'])
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
        
        # 训练模型
        train_losses = []
        best_loss = float('inf')
        patience = 20
        patience_counter = 0
        
        print("开始训练...")
        for epoch in range(params['epochs']):
            model.train()
            total_loss = 0
            
            # 创建批次
            for i in range(0, len(X_train), params['batch_size']):
                batch_X = X_train[i:i+params['batch_size']]
                batch_y = y_train[i:i+params['batch_size']]
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs.squeeze(), batch_y)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / (len(X_train) // params['batch_size'])
            train_losses.append(avg_loss)
            
            # 学习率调度
            scheduler.step(avg_loss)
            
            # 早停检查
            if avg_loss < best_loss:
                best_loss = avg_loss
                patience_counter = 0
                # 保存最佳模型
                best_model_path = os.path.join(self.models_dir, f'lstm_{dataset_name}_best.pth')
                torch.save(model.state_dict(), best_model_path)
            else:
                patience_counter += 1
            
            if epoch % 10 == 0:
                print(f'Epoch [{epoch}/{params["epochs"]}], Loss: {avg_loss:.6f}, LR: {optimizer.param_groups[0]["lr"]:.6f}')
            
            if patience_counter >= patience:
                print(f"早停触发，在第 {epoch} 轮停止训练")
                break
        
        # 加载最佳模型进行评估
        model.load_state_dict(torch.load(best_model_path))
        
        # 评估模型
        model.eval()
        with torch.no_grad():
            train_pred = model(X_train).cpu().numpy()
            test_pred = model(X_test).cpu().numpy()
        
        # 反归一化
        train_pred = scaler.inverse_transform(train_pred)
        test_pred = scaler.inverse_transform(test_pred)
        y_train_actual = scaler.inverse_transform(y_train.cpu().numpy().reshape(-1, 1))
        y_test_actual = scaler.inverse_transform(y_test.cpu().numpy().reshape(-1, 1))
        
        # 计算指标
        train_mse = mean_squared_error(y_train_actual, train_pred)
        test_mse = mean_squared_error(y_test_actual, test_pred)
        train_mae = mean_absolute_error(y_train_actual, train_pred)
        test_mae = mean_absolute_error(y_test_actual, test_pred)
        train_r2 = r2_score(y_train_actual, train_pred)
        test_r2 = r2_score(y_test_actual, test_pred)
        
        # 打印结果
        print(f"\\n训练结果:")
        print(f"训练集 - MSE: {train_mse:.6f}, MAE: {train_mae:.6f}, R²: {train_r2:.4f}")
        print(f"测试集 - MSE: {test_mse:.6f}, MAE: {test_mae:.6f}, R²: {test_r2:.4f}")
        
        # 保存结果
        results = {
            'model_type': 'LSTM',
            'dataset': dataset_name,
            'hyperparameters': params,
            'metrics': {
                'train_mse': float(train_mse),
                'test_mse': float(test_mse),
                'train_mae': float(train_mae),
                'test_mae': float(test_mae),
                'train_r2': float(train_r2),
                'test_r2': float(test_r2)
            },
            'training_history': {
                'losses': train_losses
            },
            'model_path': best_model_path,
            'scaler_params': {
                'data_min_': scaler.data_min_.tolist(),
                'data_max_': scaler.data_max_.tolist(),
                'data_range_': scaler.data_range_.tolist()
            }
        }
        
        # 保存结果文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = os.path.join(self.results_dir, f'lstm_{dataset_name}_{timestamp}.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 生成可视化
        self.visualize_lstm_results(results, train_pred, test_pred, y_train_actual, y_test_actual, timestamp, dataset_name)
        
        print(f"结果已保存: {results_path}")
        return results
    
    def visualize_lstm_results(self, results, train_pred, test_pred, y_train_actual, y_test_actual, timestamp, dataset_name):
        """可视化LSTM训练结果"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'LSTM模型训练结果 - {dataset_name}', fontsize=16)
        
        # 训练损失曲线
        axes[0, 0].plot(results['training_history']['losses'])
        axes[0, 0].set_title('训练损失曲线')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].grid(True)
        
        # 训练集预测vs实际
        sample_size = min(500, len(train_pred))
        axes[0, 1].plot(y_train_actual[:sample_size], label='实际值', alpha=0.7)
        axes[0, 1].plot(train_pred[:sample_size], label='预测值', alpha=0.7)
        axes[0, 1].set_title(f'训练集预测 (R²: {results["metrics"]["train_r2"]:.4f})')
        axes[0, 1].set_xlabel('样本')
        axes[0, 1].set_ylabel('值')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # 测试集预测vs实际
        sample_size = min(500, len(test_pred))
        axes[1, 0].plot(y_test_actual[:sample_size], label='实际值', alpha=0.7)
        axes[1, 0].plot(test_pred[:sample_size], label='预测值', alpha=0.7)
        axes[1, 0].set_title(f'测试集预测 (R²: {results["metrics"]["test_r2"]:.4f})')
        axes[1, 0].set_xlabel('样本')
        axes[1, 0].set_ylabel('值')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # 散点图：预测vs实际
        axes[1, 1].scatter(y_test_actual, test_pred, alpha=0.5)
        min_val = min(y_test_actual.min(), test_pred.min())
        max_val = max(y_test_actual.max(), test_pred.max())
        axes[1, 1].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        axes[1, 1].set_title('预测值 vs 实际值')
        axes[1, 1].set_xlabel('实际值')
        axes[1, 1].set_ylabel('预测值')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        # 保存图片
        plot_path = os.path.join(self.results_dir, f'lstm_{dataset_name}_{timestamp}.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"可视化结果已保存: {plot_path}")
    
    def train_simple_transformer(self, dataset_name, hyperparameters=None):
        """训练简单的Transformer模型（模拟Qwen）"""
        print(f"\\n{'='*60}")
        print(f"开始训练Transformer模型 - {dataset_name}")
        print(f"{'='*60}")
        
        # 默认超参数
        default_params = {
            'sequence_length': 60,
            'hidden_size': 256,
            'num_heads': 8,
            'num_layers': 4,
            'learning_rate': 0.0001,
            'batch_size': 16,
            'epochs': 50,
            'test_size': 0.2
        }
        
        if hyperparameters:
            default_params.update(hyperparameters)
        
        params = default_params
        print(f"使用超参数: {params}")
        
        # 加载数据
        dataset_path = os.path.join(self.data_dir, f"{dataset_name}.csv")
        df = pd.read_csv(dataset_path)
        
        # 确保有value列
        if 'value' in df.columns:
            data = df['value']
        else:
            # 使用第一个数值列
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            data = df[numeric_cols[0]]
        
        print(f"数据形状: {data.shape}")
        
        # 准备数据（重用LSTM的数据准备函数）
        X_train, y_train, X_test, y_test, scaler = self.prepare_lstm_data(
            data, params['sequence_length'], params['test_size']
        )
        
        # 创建简单的Transformer模型
        class SimpleTransformer(nn.Module):
            def __init__(self, input_size, hidden_size, num_heads, num_layers, output_size):
                super(SimpleTransformer, self).__init__()
                self.input_projection = nn.Linear(input_size, hidden_size)
                self.positional_encoding = nn.Parameter(torch.randn(1000, hidden_size))
                
                encoder_layers = nn.TransformerEncoderLayer(
                    d_model=hidden_size,
                    nhead=num_heads,
                    dim_feedforward=hidden_size * 4,
                    dropout=0.1,
                    batch_first=True
                )
                self.transformer = nn.TransformerEncoder(encoder_layers, num_layers)
                self.output_projection = nn.Linear(hidden_size, output_size)
                self.dropout = nn.Dropout(0.1)
                
            def forward(self, x):
                seq_len = x.size(1)
                
                # 输入投影
                x = self.input_projection(x)
                
                # 添加位置编码
                x = x + self.positional_encoding[:seq_len, :].unsqueeze(0)
                
                # Transformer编码
                x = self.transformer(x)
                
                # 取最后一个时间步
                x = x[:, -1, :]
                x = self.dropout(x)
                
                # 输出投影
                x = self.output_projection(x)
                
                return x
        
        model = SimpleTransformer(
            input_size=1,
            hidden_size=params['hidden_size'],
            num_heads=params['num_heads'],
            num_layers=params['num_layers'],
            output_size=1
        ).to(self.device)
        
        print(f"模型参数数量: {sum(p.numel() for p in model.parameters()):,}")
        
        # 训练过程（类似LSTM）
        criterion = nn.MSELoss()
        optimizer = torch.optim.AdamW(model.parameters(), lr=params['learning_rate'], weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
        
        train_losses = []
        best_loss = float('inf')
        patience = 15
        patience_counter = 0
        
        print("开始训练...")
        for epoch in range(params['epochs']):
            model.train()
            total_loss = 0
            
            for i in range(0, len(X_train), params['batch_size']):
                batch_X = X_train[i:i+params['batch_size']]
                batch_y = y_train[i:i+params['batch_size']]
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs.squeeze(), batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / (len(X_train) // params['batch_size'])
            train_losses.append(avg_loss)
            scheduler.step(avg_loss)
            
            if avg_loss < best_loss:
                best_loss = avg_loss
                patience_counter = 0
                best_model_path = os.path.join(self.models_dir, f'transformer_{dataset_name}_best.pth')
                torch.save(model.state_dict(), best_model_path)
            else:
                patience_counter += 1
            
            if epoch % 10 == 0:
                print(f'Epoch [{epoch}/{params["epochs"]}], Loss: {avg_loss:.6f}')
            
            if patience_counter >= patience:
                print(f"早停触发，在第 {epoch} 轮停止训练")
                break
        
        # 评估模型
        model.load_state_dict(torch.load(best_model_path))
        model.eval()
        with torch.no_grad():
            train_pred = model(X_train).cpu().numpy()
            test_pred = model(X_test).cpu().numpy()
        
        # 反归一化
        train_pred = scaler.inverse_transform(train_pred)
        test_pred = scaler.inverse_transform(test_pred)
        y_train_actual = scaler.inverse_transform(y_train.cpu().numpy().reshape(-1, 1))
        y_test_actual = scaler.inverse_transform(y_test.cpu().numpy().reshape(-1, 1))
        
        # 计算指标
        train_mse = mean_squared_error(y_train_actual, train_pred)
        test_mse = mean_squared_error(y_test_actual, test_pred)
        train_mae = mean_absolute_error(y_train_actual, train_pred)
        test_mae = mean_absolute_error(y_test_actual, test_pred)
        train_r2 = r2_score(y_train_actual, train_pred)
        test_r2 = r2_score(y_test_actual, test_pred)
        
        print(f"\\n训练结果:")
        print(f"训练集 - MSE: {train_mse:.6f}, MAE: {train_mae:.6f}, R²: {train_r2:.4f}")
        print(f"测试集 - MSE: {test_mse:.6f}, MAE: {test_mae:.6f}, R²: {test_r2:.4f}")
        
        # 保存结果
        results = {
            'model_type': 'Transformer',
            'dataset': dataset_name,
            'hyperparameters': params,
            'metrics': {
                'train_mse': float(train_mse),
                'test_mse': float(test_mse),
                'train_mae': float(train_mae),
                'test_mae': float(test_mae),
                'train_r2': float(train_r2),
                'test_r2': float(test_r2)
            },
            'training_history': {
                'losses': train_losses
            },
            'model_path': best_model_path
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = os.path.join(self.results_dir, f'transformer_{dataset_name}_{timestamp}.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存: {results_path}")
        return results
    
    def run_full_experiment(self):
        """运行完整的实验"""
        print("TimeVis 模型微调实验")
        print("=" * 60)
        
        # 加载数据集
        datasets = self.load_datasets()
        
        if not datasets:
            print("未找到可用的数据集，请先运行 data_processing.py")
            return
        
        all_results = []
        
        for dataset_info in datasets:
            dataset_name = dataset_info['name']
            print(f"\\n处理数据集: {dataset_name}")
            
            # 训练LSTM模型
            try:
                lstm_results = self.train_lstm_model(dataset_name)
                all_results.append(lstm_results)
            except Exception as e:
                print(f"LSTM训练失败: {e}")
            
            # 训练Transformer模型
            try:
                transformer_results = self.train_simple_transformer(dataset_name)
                all_results.append(transformer_results)
            except Exception as e:
                print(f"Transformer训练失败: {e}")
        
        # 生成比较报告
        self.generate_comparison_report(all_results)
        
        print("\\n" + "=" * 60)
        print("实验完成！")
        print("=" * 60)
    
    def generate_comparison_report(self, results):
        """生成模型比较报告"""
        if not results:
            return
        
        print("\\n生成模型比较报告...")
        
        # 创建比较表格
        comparison_data = []
        for result in results:
            comparison_data.append({
                '模型类型': result['model_type'],
                '数据集': result['dataset'],
                '测试MSE': result['metrics']['test_mse'],
                '测试MAE': result['metrics']['test_mae'],
                '测试R²': result['metrics']['test_r2']
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # 保存比较结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_path = os.path.join(self.results_dir, f'model_comparison_{timestamp}.csv')
        df_comparison.to_csv(comparison_path, index=False, encoding='utf-8-sig')
        
        print(f"\\n模型比较结果:")
        print(df_comparison.to_string(index=False))
        print(f"\\n比较报告已保存: {comparison_path}")

def main():
    """主函数"""
    print("TimeVis 模型微调工具")
    print("支持LSTM和Transformer模型的微调训练")
    print("=" * 60)
    
    # 创建微调器
    tuner = ModelFineTuner()
    
    # 运行完整实验
    tuner.run_full_experiment()

if __name__ == "__main__":
    main()
