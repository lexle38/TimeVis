from celery import Celery
from datetime import datetime
import os
import json
from typing import Dict, Optional
from loguru import logger

from app.models import db, Task, Model as ModelRecord
from utils.model_trainer import ModelTrainer, ModelPredictor
from utils.data_processor import TimeSeriesProcessor
from config.config import Config

# 创建Celery实例
celery = Celery('timevis')
celery.conf.update(
    broker_url=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

@celery.task(bind=True)
def training_task(self, task_id: int, data_path: str, model_config: Dict, 
                 data_type: str, model_type: str):
    """训练模型的Celery任务"""
    
    try:
        logger.info(f"开始执行训练任务: {task_id}, 模型类型: {model_type}, 数据类型: {data_type}")
        
        # 更新任务状态
        task_record = Task.query.get(task_id)
        if not task_record:
            raise ValueError(f"任务 {task_id} 不存在")
        
        task_record.status = 'running'
        task_record.started_at = datetime.utcnow()
        task_record.progress = 0.1
        db.session.commit()
        
        # 初始化训练器
        trainer = ModelTrainer(working_dir=f"./workspace/task_{task_id}")
        
        # 准备数据
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': '准备数据中...'})
        task_record.progress = 0.2
        db.session.commit()
        
        # 确定目标列
        processor = TimeSeriesProcessor()
        df = processor.load_data(data_path)
        target_column = df.select_dtypes(include=['number']).columns[0]  # 使用第一个数值列
        
        data_info = trainer.prepare_data(
            data_path=data_path,
            data_type=data_type,
            target_column=target_column,
            sequence_length=model_config.get('sequence_length', 10)
        )
        
        # 训练模型
        self.update_state(state='PROGRESS', meta={'progress': 40, 'status': '开始训练模型...'})
        task_record.progress = 0.4
        db.session.commit()
        
        if model_type == 'qwen':
            results = trainer.train_qwen_model(
                data_info=data_info,
                model_config=model_config,
                data_type=data_type,
                task_id=str(task_id)
            )
        elif model_type == 'lstm':
            results = trainer.train_lstm_model(
                data_info=data_info,
                model_config=model_config,
                data_type=data_type,
                task_id=str(task_id)
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 保存模型记录
        self.update_state(state='PROGRESS', meta={'progress': 90, 'status': '保存模型信息...'})
        task_record.progress = 0.9
        db.session.commit()
        
        model_record = ModelRecord(
            name=f"{model_type}_{data_type}_{task_id}",
            model_type=model_type,
            data_type=data_type,
            model_path=results['model_path'],
            training_task_id=task_id,
            training_parameters=json.dumps(model_config),
            validation_mse=results['metrics']['mse'],
            validation_mae=results['metrics']['mae'],
            validation_rmse=results['metrics']['rmse']
        )
        
        db.session.add(model_record)
        
        # 更新任务状态
        task_record.status = 'completed'
        task_record.completed_at = datetime.utcnow()
        task_record.progress = 1.0
        task_record.model_file_path = results['model_path']
        task_record.mse = results['metrics']['mse']
        task_record.mae = results['metrics']['mae'] 
        task_record.rmse = results['metrics']['rmse']
        
        # 保存结果文件路径
        results_file = os.path.join(trainer.working_dir, "results", f"{model_type}_{data_type}_{task_id}_results.json")
        task_record.result_file_path = results_file
        
        db.session.commit()
        
        logger.info(f"训练任务 {task_id} 完成成功")
        
        return {
            'status': 'completed',
            'results': results,
            'model_id': model_record.id
        }
        
    except Exception as e:
        logger.error(f"训练任务 {task_id} 失败: {e}")
        
        # 更新任务状态为失败
        task_record = Task.query.get(task_id)
        if task_record:
            task_record.status = 'failed'
            task_record.error_message = str(e)
            task_record.completed_at = datetime.utcnow()
            db.session.commit()
        
        # 更新Celery任务状态
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'task_id': task_id
            }
        )
        
        raise

@celery.task(bind=True)
def prediction_task(self, task_id: int, model_id: int, input_data: Dict):
    """预测任务"""
    
    try:
        logger.info(f"开始执行预测任务: {task_id}, 模型ID: {model_id}")
        
        # 更新任务状态
        task_record = Task.query.get(task_id)
        if not task_record:
            raise ValueError(f"任务 {task_id} 不存在")
        
        task_record.status = 'running'
        task_record.started_at = datetime.utcnow()
        task_record.progress = 0.1
        db.session.commit()
        
        # 获取模型信息
        model_record = ModelRecord.query.get(model_id)
        if not model_record:
            raise ValueError(f"模型 {model_id} 不存在")
        
        # 初始化预测器
        predictor = ModelPredictor()
        
        # 加载模型
        self.update_state(state='PROGRESS', meta={'progress': 30, 'status': '加载模型...'})
        task_record.progress = 0.3
        db.session.commit()
        
        if model_record.model_type == 'qwen':
            predictor.load_qwen_model(model_record.model_path)
        elif model_record.model_type == 'lstm':
            predictor.load_lstm_model(model_record.model_path)
        else:
            raise ValueError(f"不支持的模型类型: {model_record.model_type}")
        
        # 执行预测
        self.update_state(state='PROGRESS', meta={'progress': 60, 'status': '执行预测...'})
        task_record.progress = 0.6
        db.session.commit()
        
        input_sequence = input_data['sequence']
        prediction = predictor.predict(
            model_type=model_record.model_type,
            input_sequence=input_sequence,
            data_type=model_record.data_type
        )
        
        # 保存预测结果
        self.update_state(state='PROGRESS', meta={'progress': 90, 'status': '保存结果...'})
        task_record.progress = 0.9
        db.session.commit()
        
        results = {
            'input_sequence': input_sequence,
            'prediction': prediction,
            'model_type': model_record.model_type,
            'data_type': model_record.data_type,
            'model_id': model_id,
            'prediction_time': datetime.utcnow().isoformat()
        }
        
        # 保存结果文件
        results_dir = f"./workspace/task_{task_id}/results"
        os.makedirs(results_dir, exist_ok=True)
        results_file = os.path.join(results_dir, f"prediction_{task_id}_results.json")
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # 更新任务状态
        task_record.status = 'completed'
        task_record.completed_at = datetime.utcnow()
        task_record.progress = 1.0
        task_record.result_file_path = results_file
        
        db.session.commit()
        
        logger.info(f"预测任务 {task_id} 完成成功，预测结果: {prediction}")
        
        return {
            'status': 'completed',
            'results': results
        }
        
    except Exception as e:
        logger.error(f"预测任务 {task_id} 失败: {e}")
        
        # 更新任务状态为失败
        task_record = Task.query.get(task_id)
        if task_record:
            task_record.status = 'failed'
            task_record.error_message = str(e)
            task_record.completed_at = datetime.utcnow()
            db.session.commit()
        
        # 更新Celery任务状态
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'task_id': task_id
            }
        )
        
        raise

@celery.task(bind=True)
def model_comparison_task(self, task_id: int, qwen_model_id: int, lstm_model_id: int, 
                         test_data_path: str):
    """模型比较任务"""
    
    try:
        logger.info(f"开始执行模型比较任务: {task_id}")
        
        # 更新任务状态
        task_record = Task.query.get(task_id)
        if not task_record:
            raise ValueError(f"任务 {task_id} 不存在")
        
        task_record.status = 'running'
        task_record.started_at = datetime.utcnow()
        task_record.progress = 0.1
        db.session.commit()
        
        # 获取模型信息
        qwen_model = ModelRecord.query.get(qwen_model_id)
        lstm_model = ModelRecord.query.get(lstm_model_id)
        
        if not qwen_model or not lstm_model:
            raise ValueError("模型不存在")
        
        # 初始化预测器
        predictor = ModelPredictor()
        
        # 加载模型
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': '加载模型...'})
        predictor.load_qwen_model(qwen_model.model_path)
        predictor.load_lstm_model(lstm_model.model_path)
        task_record.progress = 0.3
        db.session.commit()
        
        # 准备测试数据
        self.update_state(state='PROGRESS', meta={'progress': 40, 'status': '准备测试数据...'})
        processor = TimeSeriesProcessor()
        test_df = processor.load_data(test_data_path)
        
        # 创建测试序列
        target_column = test_df.select_dtypes(include=['number']).columns[0]
        X_test, y_test = processor.create_sequences(test_df, target_column, sequence_length=10)
        
        task_record.progress = 0.5
        db.session.commit()
        
        # 执行预测
        self.update_state(state='PROGRESS', meta={'progress': 60, 'status': '执行预测...'})
        
        qwen_predictions = []
        lstm_predictions = []
        
        for i, seq in enumerate(X_test):
            if i % 10 == 0:  # 更新进度
                progress = 0.6 + 0.25 * (i / len(X_test))
                task_record.progress = progress
                db.session.commit()
            
            qwen_pred = predictor.predict('qwen', seq.tolist(), qwen_model.data_type)
            lstm_pred = predictor.predict('lstm', seq.tolist())
            
            qwen_predictions.append(qwen_pred)
            lstm_predictions.append(lstm_pred)
        
        # 计算比较指标
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        import numpy as np
        
        qwen_mse = mean_squared_error(y_test, qwen_predictions)
        qwen_mae = mean_absolute_error(y_test, qwen_predictions)
        qwen_rmse = np.sqrt(qwen_mse)
        
        lstm_mse = mean_squared_error(y_test, lstm_predictions)
        lstm_mae = mean_absolute_error(y_test, lstm_predictions)
        lstm_rmse = np.sqrt(lstm_mse)
        
        # 生成比较结果
        comparison_results = {
            'qwen_metrics': {
                'mse': float(qwen_mse),
                'mae': float(qwen_mae),
                'rmse': float(qwen_rmse)
            },
            'lstm_metrics': {
                'mse': float(lstm_mse),
                'mae': float(lstm_mae),
                'rmse': float(lstm_rmse)
            },
            'predictions': {
                'qwen': qwen_predictions,
                'lstm': lstm_predictions,
                'actual': y_test.tolist()
            },
            'comparison_time': datetime.utcnow().isoformat()
        }
        
        # 保存结果
        self.update_state(state='PROGRESS', meta={'progress': 90, 'status': '保存结果...'})
        
        results_dir = f"./workspace/task_{task_id}/results"
        os.makedirs(results_dir, exist_ok=True)
        results_file = os.path.join(results_dir, f"comparison_{task_id}_results.json")
        
        with open(results_file, 'w') as f:
            json.dump(comparison_results, f, indent=2, default=str)
        
        # 更新任务状态
        task_record.status = 'completed'
        task_record.completed_at = datetime.utcnow()
        task_record.progress = 1.0
        task_record.result_file_path = results_file
        
        db.session.commit()
        
        logger.info(f"模型比较任务 {task_id} 完成成功")
        
        return {
            'status': 'completed',
            'results': comparison_results
        }
        
    except Exception as e:
        logger.error(f"模型比较任务 {task_id} 失败: {e}")
        
        # 更新任务状态为失败
        task_record = Task.query.get(task_id)
        if task_record:
            task_record.status = 'failed'
            task_record.error_message = str(e)
            task_record.completed_at = datetime.utcnow()
            db.session.commit()
        
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'task_id': task_id
            }
        )
        
        raise

@celery.task
def cleanup_old_tasks():
    """清理旧任务和文件"""
    
    try:
        # 删除7天前的已完成任务
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        old_tasks = Task.query.filter(
            Task.completed_at < cutoff_date,
            Task.status.in_(['completed', 'failed'])
        ).all()
        
        for task in old_tasks:
            # 删除相关文件
            if task.result_file_path and os.path.exists(task.result_file_path):
                try:
                    os.remove(task.result_file_path)
                except:
                    pass
            
            # 删除任务记录
            db.session.delete(task)
        
        db.session.commit()
        
        logger.info(f"清理了 {len(old_tasks)} 个旧任务")
        
        return {'cleaned_tasks': len(old_tasks)}
        
    except Exception as e:
        logger.error(f"清理任务失败: {e}")
        raise
