import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os
import pickle
import json
from typing import Tuple, List, Optional
from loguru import logger

class TimeSeriesDataset(Dataset):
    """时间序列数据集"""
    
    def __init__(self, data: np.ndarray, sequence_length: int):
        self.data = data
        self.sequence_length = sequence_length
    
    def __len__(self):
        return len(self.data) - self.sequence_length
    
    def __getitem__(self, idx):
        x = self.data[idx:idx + self.sequence_length]
        y = self.data[idx + self.sequence_length]
        return torch.FloatTensor(x), torch.FloatTensor([y])

class LSTMTimeSeriesModel(nn.Module):
    """LSTM时间序列预测模型"""
    
    def __init__(self, input_size: int = 1, hidden_size: int = 64, 
                 num_layers: int = 2, dropout: float = 0.2, output_size: int = 1):
        super(LSTMTimeSeriesModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.input_size = input_size
        self.output_size = output_size
        
        # LSTM层
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # 全连接层
        self.fc = nn.Linear(hidden_size, output_size)
        
        # Dropout层
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # 初始化隐藏状态
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        
        # LSTM前向传播
        lstm_out, _ = self.lstm(x, (h0, c0))
        
        # 取最后一个时间步的输出
        last_output = lstm_out[:, -1, :]
        
        # Dropout
        last_output = self.dropout(last_output)
        
        # 全连接层
        output = self.fc(last_output)
        
        return output

class LSTMPredictor:
    """LSTM预测器封装类"""
    
    def __init__(self, sequence_length: int = 10, hidden_size: int = 64, 
                 num_layers: int = 2, dropout: float = 0.2):
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        
        self.model = None
        self.scaler = MinMaxScaler()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.is_trained = False
        
        logger.info(f"初始化LSTM预测器，设备: {self.device}")
    
    def prepare_data(self, data: pd.DataFrame, train_ratio: float = 0.8) -> Tuple[DataLoader, DataLoader, np.ndarray]:
        """准备训练和测试数据"""
        
        # 提取数值列（假设第一列是目标变量）
        values = data.iloc[:, 0].values.reshape(-1, 1)
        
        # 数据归一化
        scaled_data = self.scaler.fit_transform(values)
        
        # 划分训练和测试集
        train_size = int(len(scaled_data) * train_ratio)
        train_data = scaled_data[:train_size]
        test_data = scaled_data[train_size:]
        
        # 创建数据集
        train_dataset = TimeSeriesDataset(train_data.flatten(), self.sequence_length)
        test_dataset = TimeSeriesDataset(test_data.flatten(), self.sequence_length)
        
        # 创建数据加载器
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        logger.info(f"数据准备完成 - 训练样本: {len(train_dataset)}, 测试样本: {len(test_dataset)}")
        
        return train_loader, test_loader, scaled_data
    
    def build_model(self):
        """构建模型"""
        self.model = LSTMTimeSeriesModel(
            input_size=1,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
            output_size=1
        ).to(self.device)
        
        logger.info(f"模型构建完成: {sum(p.numel() for p in self.model.parameters())} 参数")
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              num_epochs: int = 100, learning_rate: float = 0.001,
              patience: int = 10) -> dict:
        """训练模型"""
        
        if self.model is None:
            self.build_model()
        
        # 损失函数和优化器
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
        
        # 训练历史
        train_losses = []
        val_losses = []
        best_val_loss = float('inf')
        patience_counter = 0
        
        logger.info("开始训练...")
        
        for epoch in range(num_epochs):
            # 训练阶段
            self.model.train()
            train_loss = 0.0
            
            for batch_x, batch_y in train_loader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                
                # 添加特征维度
                batch_x = batch_x.unsqueeze(-1)
                
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                
                # 梯度裁剪
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                train_loss += loss.item()
            
            # 验证阶段
            self.model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                    batch_x = batch_x.unsqueeze(-1)
                    
                    outputs = self.model(batch_x)
                    loss = criterion(outputs, batch_y)
                    val_loss += loss.item()
            
            # 计算平均损失
            avg_train_loss = train_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)
            
            train_losses.append(avg_train_loss)
            val_losses.append(avg_val_loss)
            
            # 学习率调度
            scheduler.step(avg_val_loss)
            
            # 早停检查
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                patience_counter = 0
            else:
                patience_counter += 1
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}/{num_epochs}, Train Loss: {avg_train_loss:.6f}, Val Loss: {avg_val_loss:.6f}")
            
            if patience_counter >= patience:
                logger.info(f"早停触发，在第 {epoch} 轮停止训练")
                break
        
        self.is_trained = True
        logger.info("训练完成")
        
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'best_val_loss': best_val_loss,
            'final_epoch': epoch
        }
    
    def predict_single(self, input_sequence: List[float]) -> float:
        """单次预测"""
        if self.model is None or not self.is_trained:
            raise ValueError("模型未训练")
        
        self.model.eval()
        
        # 数据预处理
        input_array = np.array(input_sequence).reshape(-1, 1)
        scaled_input = self.scaler.transform(input_array)
        
        # 转换为张量
        input_tensor = torch.FloatTensor(scaled_input.flatten()).unsqueeze(0).unsqueeze(-1).to(self.device)
        
        # 预测
        with torch.no_grad():
            prediction = self.model(input_tensor)
        
        # 反归一化
        prediction_scaled = prediction.cpu().numpy().reshape(-1, 1)
        prediction_original = self.scaler.inverse_transform(prediction_scaled)
        
        return float(prediction_original[0, 0])
    
    def predict_batch(self, sequences: List[List[float]]) -> List[float]:
        """批量预测"""
        predictions = []
        for seq in sequences:
            pred = self.predict_single(seq)
            predictions.append(pred)
        return predictions
    
    def evaluate(self, test_loader: DataLoader) -> dict:
        """评估模型"""
        if self.model is None or not self.is_trained:
            raise ValueError("模型未训练")
        
        self.model.eval()
        
        predictions = []
        actuals = []
        
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                batch_x = batch_x.unsqueeze(-1)
                
                outputs = self.model(batch_x)
                
                # 反归一化
                pred_scaled = outputs.cpu().numpy()
                actual_scaled = batch_y.cpu().numpy()
                
                pred_original = self.scaler.inverse_transform(pred_scaled)
                actual_original = self.scaler.inverse_transform(actual_scaled)
                
                predictions.extend(pred_original.flatten())
                actuals.extend(actual_original.flatten())
        
        # 计算指标
        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        rmse = np.sqrt(mse)
        
        logger.info(f"评估结果 - MSE: {mse:.6f}, MAE: {mae:.6f}, RMSE: {rmse:.6f}")
        
        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'predictions': predictions,
            'actuals': actuals
        }
    
    def save_model(self, save_path: str):
        """保存模型"""
        if self.model is None:
            raise ValueError("没有可保存的模型")
        
        os.makedirs(save_path, exist_ok=True)
        
        # 保存模型状态字典
        model_path = os.path.join(save_path, 'lstm_model.pth')
        torch.save(self.model.state_dict(), model_path)
        
        # 保存归一化器
        scaler_path = os.path.join(save_path, 'scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # 保存配置
        config = {
            'sequence_length': self.sequence_length,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'dropout': self.dropout,
            'is_trained': self.is_trained
        }
        
        config_path = os.path.join(save_path, 'model_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"模型已保存至: {save_path}")
    
    def load_model(self, model_path: str):
        """加载模型"""
        try:
            # 加载配置
            config_path = os.path.join(model_path, 'model_config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.sequence_length = config['sequence_length']
            self.hidden_size = config['hidden_size']
            self.num_layers = config['num_layers']
            self.dropout = config['dropout']
            self.is_trained = config['is_trained']
            
            # 构建模型
            self.build_model()
            
            # 加载模型权重
            model_state_path = os.path.join(model_path, 'lstm_model.pth')
            self.model.load_state_dict(torch.load(model_state_path, map_location=self.device))
            
            # 加载归一化器
            scaler_path = os.path.join(model_path, 'scaler.pkl')
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            logger.info(f"模型加载成功: {model_path}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
