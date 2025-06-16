from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Task(db.Model):
    """训练和预测任务记录"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(20), nullable=False)  # 'training' or 'prediction'
    data_type = db.Column(db.String(20), nullable=False)  # 'weather', 'electricity', 'traffic'
    model_type = db.Column(db.String(20), nullable=False)  # 'qwen', 'lstm'
    
    status = db.Column(db.String(20), default='pending')  # 'pending', 'running', 'completed', 'failed'
    progress = db.Column(db.Float, default=0.0)
    
    # 任务参数
    parameters = db.Column(db.Text)  # JSON string of parameters
    
    # 文件路径
    data_file_path = db.Column(db.String(255))
    model_file_path = db.Column(db.String(255))
    result_file_path = db.Column(db.String(255))
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # 结果指标
    mse = db.Column(db.Float)
    mae = db.Column(db.Float)
    rmse = db.Column(db.Float)
    
    # 错误信息
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'data_type': self.data_type,
            'model_type': self.model_type,
            'status': self.status,
            'progress': self.progress,
            'parameters': json.loads(self.parameters) if self.parameters else {},
            'data_file_path': self.data_file_path,
            'model_file_path': self.model_file_path,
            'result_file_path': self.result_file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'mse': self.mse,
            'mae': self.mae,
            'rmse': self.rmse,
            'error_message': self.error_message
        }

class Model(db.Model):
    """模型记录"""
    __tablename__ = 'models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(20), nullable=False)  # 'qwen', 'lstm'
    data_type = db.Column(db.String(20), nullable=False)  # 'weather', 'electricity', 'traffic'
    
    # 模型文件路径
    model_path = db.Column(db.String(255), nullable=False)
    config_path = db.Column(db.String(255))
    
    # 训练信息
    training_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    training_parameters = db.Column(db.Text)  # JSON string
    
    # 性能指标
    validation_mse = db.Column(db.Float)
    validation_mae = db.Column(db.Float)
    validation_rmse = db.Column(db.Float)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'data_type': self.data_type,
            'model_path': self.model_path,
            'config_path': self.config_path,
            'training_task_id': self.training_task_id,
            'training_parameters': json.loads(self.training_parameters) if self.training_parameters else {},
            'validation_mse': self.validation_mse,
            'validation_mae': self.validation_mae,
            'validation_rmse': self.validation_rmse,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class Dataset(db.Model):
    """数据集记录"""
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.String(20), nullable=False)  # 'weather', 'electricity', 'traffic'
    
    # 文件信息
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # bytes
    
    # 数据统计
    num_samples = db.Column(db.Integer)
    num_features = db.Column(db.Integer)
    time_range_start = db.Column(db.DateTime)
    time_range_end = db.Column(db.DateTime)
    
    # 预处理信息
    preprocessing_config = db.Column(db.Text)  # JSON string
    
    # 时间戳
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'data_type': self.data_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'num_samples': self.num_samples,
            'num_features': self.num_features,
            'time_range_start': self.time_range_start.isoformat() if self.time_range_start else None,
            'time_range_end': self.time_range_end.isoformat() if self.time_range_end else None,
            'preprocessing_config': json.loads(self.preprocessing_config) if self.preprocessing_config else {},
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
