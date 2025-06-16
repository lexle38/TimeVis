import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger

from models.qwen_model import QwenTimeSeriesModel
from models.lstm_model import LSTMPredictor
from utils.data_processor import TimeSeriesProcessor, DataValidator

class ModelTrainer:
    """模型训练器"""
    
    def __init__(self, working_dir: str = "./work_space"):
        self.working_dir = working_dir
        self.data_processor = TimeSeriesProcessor()
        self.validator = DataValidator()
        
        # 创建工作目录
        os.makedirs(working_dir, exist_ok=True)
        os.makedirs(os.path.join(working_dir, "models"), exist_ok=True)
        os.makedirs(os.path.join(working_dir, "data"), exist_ok=True)
        os.makedirs(os.path.join(working_dir, "results"), exist_ok=True)
        
    def prepare_data(self, data_path: str, data_type: str, 
                    target_column: str, sequence_length: int = 10) -> Dict:
        """准备训练数据"""
        
        logger.info(f"开始准备数据: {data_path}")
        
        # 加载数据
        df = self.data_processor.load_data(data_path)
        
        # 数据验证
        validation_results = self.validator.validate_time_series(df, target_column)
        if not all(validation_results.values()):
            logger.warning(f"数据验证发现问题: {validation_results}")
        
        # 数据分析
        analysis = self.data_processor.analyze_data(df)
        
        # 数据清洗
        df_cleaned = self.data_processor.clean_data(
            df, 
            remove_duplicates=True,
            fill_missing='forward',
            remove_outliers=False
        )
        
        # 创建序列
        X, y = self.data_processor.create_sequences(
            df_cleaned, 
            target_column=target_column,
            sequence_length=sequence_length
        )
        
        # 分割数据
        X_train, X_val, X_test, y_train, y_val, y_test = self.data_processor.split_data(
            X, y, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
        )
        
        # 保存处理后的数据
        processed_data_path = os.path.join(self.working_dir, "data", f"{data_type}_processed.npz")
        np.savez(
            processed_data_path,
            X_train=X_train, X_val=X_val, X_test=X_test,
            y_train=y_train, y_val=y_val, y_test=y_test
        )
        
        return {
            'processed_data_path': processed_data_path,
            'data_analysis': analysis,
            'validation_results': validation_results,
            'shapes': {
                'X_train': X_train.shape,
                'X_val': X_val.shape, 
                'X_test': X_test.shape,
                'y_train': y_train.shape,
                'y_val': y_val.shape,
                'y_test': y_test.shape
            },
            'original_data': df_cleaned
        }
    
    def train_qwen_model(self, data_info: Dict, model_config: Dict, 
                        data_type: str, task_id: str) -> Dict:
        """训练Qwen模型"""
        
        logger.info(f"开始训练Qwen模型，任务ID: {task_id}")
        
        try:
            # 加载数据
            data = np.load(data_info['processed_data_path'])
            X_train, y_train = data['X_train'], data['y_train']
            X_val, y_val = data['X_val'], data['y_val']
            X_test, y_test = data['X_test'], data['y_test']
            
            # 初始化模型
            qwen_model = QwenTimeSeriesModel(
                model_name=model_config.get('model_name', "Qwen/Qwen2.5-7B-Instruct"),
                max_length=model_config.get('max_length', 512)
            )
            
            # 加载预训练模型
            qwen_model.load_model()
            
            # 准备LoRA微调
            qwen_model.prepare_lora_model(
                r=model_config.get('lora_r', 8),
                alpha=model_config.get('lora_alpha', 32),
                dropout=model_config.get('lora_dropout', 0.1)
            )
            
            # 准备训练数据
            training_data = []
            for i in range(len(X_train)):
                training_data.extend(qwen_model.create_training_data(
                    pd.DataFrame({'value': np.concatenate([X_train[i], [y_train[i]]])}),
                    sequence_length=len(X_train[i]),
                    task_type=data_type
                ))
            
            # 模型保存路径
            model_save_path = os.path.join(self.working_dir, "models", f"qwen_{data_type}_{task_id}")
            
            # 训练模型
            qwen_model.train(
                training_data=training_data,
                output_dir=model_save_path,
                num_epochs=model_config.get('num_epochs', 3),
                learning_rate=model_config.get('learning_rate', 5e-5),
                batch_size=model_config.get('batch_size', 4),
                gradient_accumulation_steps=model_config.get('gradient_accumulation_steps', 4)
            )
            
            # 评估模型
            logger.info("开始模型评估...")
            predictions = []
            actuals = []
            
            for i in range(len(X_test)):
                pred = qwen_model.predict_single(X_test[i].tolist(), data_type)
                predictions.append(pred)
                actuals.append(y_test[i])
            
            # 计算指标
            mse = mean_squared_error(actuals, predictions)
            mae = mean_absolute_error(actuals, predictions)
            rmse = np.sqrt(mse)
            
            # 保存结果
            results = {
                'model_type': 'qwen',
                'data_type': data_type,
                'task_id': task_id,
                'model_path': model_save_path,
                'metrics': {
                    'mse': float(mse),
                    'mae': float(mae),
                    'rmse': float(rmse)
                },
                'predictions': predictions,
                'actuals': actuals,
                'training_config': model_config,
                'training_time': datetime.now().isoformat()
            }
            
            # 保存训练结果
            results_path = os.path.join(self.working_dir, "results", f"qwen_{data_type}_{task_id}_results.json")
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # 生成可视化
            self._generate_prediction_plots(results, results_path.replace('.json', '_plot.png'))
            
            logger.info(f"Qwen模型训练完成 - MSE: {mse:.6f}, MAE: {mae:.6f}, RMSE: {rmse:.6f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Qwen模型训练失败: {e}")
            raise
    
    def train_lstm_model(self, data_info: Dict, model_config: Dict, 
                        data_type: str, task_id: str) -> Dict:
        """训练LSTM模型"""
        
        logger.info(f"开始训练LSTM模型，任务ID: {task_id}")
        
        try:
            # 加载数据
            data = np.load(data_info['processed_data_path'])
            X_train, y_train = data['X_train'], data['y_train']
            X_val, y_val = data['X_val'], data['y_val']
            X_test, y_test = data['X_test'], data['y_test']
            
            # 初始化模型
            lstm_model = LSTMPredictor(
                sequence_length=model_config.get('sequence_length', 10),
                hidden_size=model_config.get('hidden_size', 64),
                num_layers=model_config.get('num_layers', 2),
                dropout=model_config.get('dropout', 0.2)
            )
            
            # 准备数据 - 使用原始数据重新处理以适应LSTM
            original_df = data_info['original_data']
            target_column = original_df.columns[0]  # 假设第一列是目标列
            
            train_loader, val_loader, scaled_data = lstm_model.prepare_data(
                original_df, train_ratio=0.8
            )
            
            # 训练模型
            training_history = lstm_model.train(
                train_loader=train_loader,
                val_loader=val_loader,
                num_epochs=model_config.get('num_epochs', 100),
                learning_rate=model_config.get('learning_rate', 0.001),
                patience=model_config.get('patience', 10)
            )
            
            # 评估模型
            evaluation_results = lstm_model.evaluate(val_loader)
            
            # 模型保存路径
            model_save_path = os.path.join(self.working_dir, "models", f"lstm_{data_type}_{task_id}")
            lstm_model.save_model(model_save_path)
            
            # 保存结果
            results = {
                'model_type': 'lstm',
                'data_type': data_type,
                'task_id': task_id,
                'model_path': model_save_path,
                'metrics': {
                    'mse': evaluation_results['mse'],
                    'mae': evaluation_results['mae'],
                    'rmse': evaluation_results['rmse']
                },
                'predictions': evaluation_results['predictions'],
                'actuals': evaluation_results['actuals'],
                'training_history': training_history,
                'training_config': model_config,
                'training_time': datetime.now().isoformat()
            }
            
            # 保存训练结果
            results_path = os.path.join(self.working_dir, "results", f"lstm_{data_type}_{task_id}_results.json")
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # 生成可视化
            self._generate_prediction_plots(results, results_path.replace('.json', '_plot.png'))
            self._generate_training_plots(training_history, results_path.replace('.json', '_training_plot.png'))
            
            logger.info(f"LSTM模型训练完成 - MSE: {evaluation_results['mse']:.6f}, MAE: {evaluation_results['mae']:.6f}, RMSE: {evaluation_results['rmse']:.6f}")
            
            return results
            
        except Exception as e:
            logger.error(f"LSTM模型训练失败: {e}")
            raise
    
    def compare_models(self, qwen_results: Dict, lstm_results: Dict, 
                      save_path: Optional[str] = None) -> Dict:
        """比较两个模型的性能"""
        
        comparison = {
            'qwen_metrics': qwen_results['metrics'],
            'lstm_metrics': lstm_results['metrics'],
            'comparison': {},
            'analysis': {}
        }
        
        # 计算性能差异
        for metric in ['mse', 'mae', 'rmse']:
            qwen_value = qwen_results['metrics'][metric]
            lstm_value = lstm_results['metrics'][metric]
            
            comparison['comparison'][metric] = {
                'qwen': qwen_value,
                'lstm': lstm_value,
                'difference': qwen_value - lstm_value,
                'relative_improvement': (lstm_value - qwen_value) / lstm_value * 100 if lstm_value != 0 else 0
            }
        
        # 分析结论
        better_model = 'qwen' if qwen_results['metrics']['mse'] < lstm_results['metrics']['mse'] else 'lstm'
        comparison['analysis']['better_model'] = better_model
        comparison['analysis']['mse_improvement'] = abs(comparison['comparison']['mse']['relative_improvement'])
        
        # 生成对比图
        if save_path:
            self._generate_comparison_plots(qwen_results, lstm_results, save_path)
        
        logger.info(f"模型比较完成，{better_model} 模型表现更好")
        
        return comparison
    
    def _generate_prediction_plots(self, results: Dict, save_path: str):
        """生成预测结果图"""
        
        predictions = results['predictions']
        actuals = results['actuals']
        model_type = results['model_type'].upper()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'{model_type} 模型预测结果分析', fontsize=16)
        
        # 预测vs实际值
        axes[0, 0].plot(actuals, label='实际值', alpha=0.7)
        axes[0, 0].plot(predictions, label='预测值', alpha=0.7)
        axes[0, 0].set_title('预测值 vs 实际值')
        axes[0, 0].set_xlabel('样本')
        axes[0, 0].set_ylabel('数值')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # 散点图
        axes[0, 1].scatter(actuals, predictions, alpha=0.6)
        axes[0, 1].plot([min(actuals), max(actuals)], [min(actuals), max(actuals)], 'r--')
        axes[0, 1].set_title('预测值 vs 实际值散点图')
        axes[0, 1].set_xlabel('实际值')
        axes[0, 1].set_ylabel('预测值')
        axes[0, 1].grid(True)
        
        # 残差图
        residuals = np.array(predictions) - np.array(actuals)
        axes[1, 0].plot(residuals)
        axes[1, 0].axhline(y=0, color='r', linestyle='--')
        axes[1, 0].set_title('残差图')
        axes[1, 0].set_xlabel('样本')
        axes[1, 0].set_ylabel('残差')
        axes[1, 0].grid(True)
        
        # 残差分布
        axes[1, 1].hist(residuals, bins=30, alpha=0.7)
        axes[1, 1].set_title('残差分布')
        axes[1, 1].set_xlabel('残差')
        axes[1, 1].set_ylabel('频次')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"预测结果图已保存: {save_path}")
    
    def _generate_training_plots(self, training_history: Dict, save_path: str):
        """生成训练过程图"""
        
        if 'train_losses' not in training_history:
            return
        
        train_losses = training_history['train_losses']
        val_losses = training_history['val_losses']
        
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, label='训练损失', alpha=0.8)
        plt.plot(val_losses, label='验证损失', alpha=0.8)
        plt.title('训练过程损失变化')
        plt.xlabel('Epoch')
        plt.ylabel('损失')
        plt.legend()
        plt.grid(True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"训练过程图已保存: {save_path}")
    
    def _generate_comparison_plots(self, qwen_results: Dict, lstm_results: Dict, save_path: str):
        """生成模型对比图"""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('模型性能对比分析', fontsize=16)
        
        # 指标对比
        metrics = ['mse', 'mae', 'rmse']
        qwen_metrics = [qwen_results['metrics'][m] for m in metrics]
        lstm_metrics = [lstm_results['metrics'][m] for m in metrics]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        axes[0, 0].bar(x - width/2, qwen_metrics, width, label='Qwen', alpha=0.8)
        axes[0, 0].bar(x + width/2, lstm_metrics, width, label='LSTM', alpha=0.8)
        axes[0, 0].set_title('性能指标对比')
        axes[0, 0].set_xlabel('指标')
        axes[0, 0].set_ylabel('数值')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels([m.upper() for m in metrics])
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # 预测结果对比（取前100个样本）
        n_samples = min(100, len(qwen_results['predictions']))
        sample_indices = range(n_samples)
        
        axes[0, 1].plot(sample_indices, qwen_results['actuals'][:n_samples], 
                       label='实际值', alpha=0.8, linewidth=2)
        axes[0, 1].plot(sample_indices, qwen_results['predictions'][:n_samples], 
                       label='Qwen预测', alpha=0.7, linestyle='--')
        axes[0, 1].plot(sample_indices, lstm_results['predictions'][:n_samples], 
                       label='LSTM预测', alpha=0.7, linestyle=':')
        axes[0, 1].set_title('预测结果对比（前100个样本）')
        axes[0, 1].set_xlabel('样本')
        axes[0, 1].set_ylabel('数值')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # 残差对比
        qwen_residuals = np.array(qwen_results['predictions']) - np.array(qwen_results['actuals'])
        lstm_residuals = np.array(lstm_results['predictions']) - np.array(lstm_results['actuals'])
        
        axes[1, 0].hist(qwen_residuals, bins=30, alpha=0.6, label='Qwen残差')
        axes[1, 0].hist(lstm_residuals, bins=30, alpha=0.6, label='LSTM残差')
        axes[1, 0].set_title('残差分布对比')
        axes[1, 0].set_xlabel('残差')
        axes[1, 0].set_ylabel('频次')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # 误差统计
        error_stats = {
            'Qwen': {
                'Mean Error': np.mean(qwen_residuals),
                'Std Error': np.std(qwen_residuals),
                'Max Error': np.max(np.abs(qwen_residuals))
            },
            'LSTM': {
                'Mean Error': np.mean(lstm_residuals),
                'Std Error': np.std(lstm_residuals),
                'Max Error': np.max(np.abs(lstm_residuals))
            }
        }
        
        # 创建误差统计表
        table_data = []
        for model, stats in error_stats.items():
            for stat, value in stats.items():
                table_data.append([model, stat, f"{value:.6f}"])
        
        axes[1, 1].axis('tight')
        axes[1, 1].axis('off')
        table = axes[1, 1].table(cellText=table_data, 
                                colLabels=['模型', '统计量', '数值'],
                                cellLoc='center',
                                loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        axes[1, 1].set_title('误差统计')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"模型对比图已保存: {save_path}")

class ModelPredictor:
    """模型预测器"""
    
    def __init__(self):
        self.qwen_model = None
        self.lstm_model = None
    
    def load_qwen_model(self, model_path: str):
        """加载Qwen模型"""
        self.qwen_model = QwenTimeSeriesModel()
        self.qwen_model.load_trained_model(model_path)
        logger.info(f"Qwen模型加载成功: {model_path}")
    
    def load_lstm_model(self, model_path: str):
        """加载LSTM模型"""
        self.lstm_model = LSTMPredictor()
        self.lstm_model.load_model(model_path)
        logger.info(f"LSTM模型加载成功: {model_path}")
    
    def predict(self, model_type: str, input_sequence: List[float], 
               data_type: str = "weather") -> float:
        """进行预测"""
        
        if model_type == 'qwen':
            if self.qwen_model is None:
                raise ValueError("Qwen模型未加载")
            return self.qwen_model.predict_single(input_sequence, data_type)
        
        elif model_type == 'lstm':
            if self.lstm_model is None:
                raise ValueError("LSTM模型未加载")
            return self.lstm_model.predict_single(input_sequence)
        
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    def batch_predict(self, model_type: str, input_sequences: List[List[float]], 
                     data_type: str = "weather") -> List[float]:
        """批量预测"""
        
        if model_type == 'qwen':
            if self.qwen_model is None:
                raise ValueError("Qwen模型未加载")
            return self.qwen_model.predict_batch(input_sequences, data_type)
        
        elif model_type == 'lstm':
            if self.lstm_model is None:
                raise ValueError("LSTM模型未加载")
            return self.lstm_model.predict_batch(input_sequences)
        
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
