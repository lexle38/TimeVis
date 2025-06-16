from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from loguru import logger

from app.models import db, Task, Model, Dataset
from app.tasks import training_task, prediction_task, model_comparison_task
from utils.data_processor import TimeSeriesProcessor, DataValidator
from config.config import Config

# 创建蓝图
api = Blueprint('api', __name__, url_prefix='/api')

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@api.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@api.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件被上传'}), 400
        
        file = request.files['file']
        data_type = request.form.get('data_type', 'weather')
        dataset_name = request.form.get('dataset_name', '')
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400
        
        # 确保上传目录存在
        upload_dir = Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)
        
        # 分析数据
        processor = TimeSeriesProcessor()
        df = processor.load_data(file_path)
        analysis = processor.analyze_data(df)
        
        # 数据验证
        validator = DataValidator()
        numeric_columns = analysis['numeric_columns']
        
        if not numeric_columns:
            return jsonify({'error': '文件中没有数值列'}), 400
        
        # 默认使用第一个数值列作为目标列
        target_column = numeric_columns[0]
        validation_results = validator.validate_time_series(df, target_column)
        
        # 创建数据集记录
        dataset = Dataset(
            name=dataset_name or filename,
            data_type=data_type,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            num_samples=analysis['shape'][0],
            num_features=analysis['shape'][1],
            preprocessing_config=json.dumps({
                'target_column': target_column,
                'numeric_columns': numeric_columns
            })
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        logger.info(f"文件上传成功: {file_path}, 数据集ID: {dataset.id}")
        
        return jsonify({
            'message': '文件上传成功',
            'dataset_id': dataset.id,
            'file_path': file_path,
            'analysis': analysis,
            'validation': validation_results,
            'target_column': target_column
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/datasets', methods=['GET'])
@cross_origin()
def get_datasets():
    """获取数据集列表"""
    try:
        datasets = Dataset.query.order_by(Dataset.uploaded_at.desc()).all()
        return jsonify({
            'datasets': [dataset.to_dict() for dataset in datasets]
        })
    except Exception as e:
        logger.error(f"获取数据集列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/datasets/<int:dataset_id>', methods=['GET'])
@cross_origin()
def get_dataset(dataset_id):
    """获取数据集详情"""
    try:
        dataset = Dataset.query.get_or_404(dataset_id)
        
        # 读取数据前几行作为预览
        processor = TimeSeriesProcessor()
        df = processor.load_data(dataset.file_path)
        preview_data = df.head(10).to_dict('records')
        
        return jsonify({
            'dataset': dataset.to_dict(),
            'preview': preview_data,
            'columns': list(df.columns),
            'shape': df.shape
        })
    except Exception as e:
        logger.error(f"获取数据集详情失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/train', methods=['POST'])
@cross_origin()
def start_training():
    """开始训练任务"""
    try:
        data = request.get_json()
        
        # 验证请求参数
        required_fields = ['dataset_id', 'model_type', 'data_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        dataset_id = data['dataset_id']
        model_type = data['model_type']
        data_type = data['data_type']
        model_config = data.get('model_config', {})
        
        # 验证参数
        if model_type not in Config.SUPPORTED_MODELS:
            return jsonify({'error': f'不支持的模型类型: {model_type}'}), 400
        
        if data_type not in Config.SUPPORTED_TASKS:
            return jsonify({'error': f'不支持的任务类型: {data_type}'}), 400
        
        # 获取数据集
        dataset = Dataset.query.get(dataset_id)
        if not dataset:
            return jsonify({'error': f'数据集 {dataset_id} 不存在'}), 404
        
        # 创建任务记录
        task = Task(
            task_type='training',
            data_type=data_type,
            model_type=model_type,
            parameters=json.dumps({
                'dataset_id': dataset_id,
                'model_config': model_config
            }),
            data_file_path=dataset.file_path
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 启动异步训练任务
        training_task.delay(
            task_id=task.id,
            data_path=dataset.file_path,
            model_config=model_config,
            data_type=data_type,
            model_type=model_type
        )
        
        logger.info(f"训练任务已启动: {task.id}")
        
        return jsonify({
            'message': '训练任务已启动',
            'task_id': task.id,
            'status': task.status
        })
        
    except Exception as e:
        logger.error(f"启动训练任务失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/predict', methods=['POST'])
@cross_origin()
def start_prediction():
    """开始预测任务"""
    try:
        data = request.get_json()
        
        # 验证请求参数
        required_fields = ['model_id', 'input_sequence']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        model_id = data['model_id']
        input_sequence = data['input_sequence']
        
        # 验证模型存在
        model = Model.query.get(model_id)
        if not model:
            return jsonify({'error': f'模型 {model_id} 不存在'}), 404
        
        # 验证输入序列
        if not isinstance(input_sequence, list) or len(input_sequence) == 0:
            return jsonify({'error': '输入序列必须是非空列表'}), 400
        
        # 创建任务记录
        task = Task(
            task_type='prediction',
            data_type=model.data_type,
            model_type=model.model_type,
            parameters=json.dumps({
                'model_id': model_id,
                'input_sequence': input_sequence
            })
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 启动异步预测任务
        prediction_task.delay(
            task_id=task.id,
            model_id=model_id,
            input_data={'sequence': input_sequence}
        )
        
        logger.info(f"预测任务已启动: {task.id}")
        
        return jsonify({
            'message': '预测任务已启动',
            'task_id': task.id,
            'status': task.status
        })
        
    except Exception as e:
        logger.error(f"启动预测任务失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/tasks', methods=['GET'])
@cross_origin()
def get_tasks():
    """获取任务列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        task_type = request.args.get('task_type')
        status = request.args.get('status')
        
        query = Task.query
        
        if task_type:
            query = query.filter(Task.task_type == task_type)
        if status:
            query = query.filter(Task.status == status)
        
        tasks = query.order_by(Task.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': tasks.total,
                'pages': tasks.pages,
                'has_next': tasks.has_next,
                'has_prev': tasks.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/tasks/<int:task_id>', methods=['GET'])
@cross_origin()
def get_task(task_id):
    """获取任务详情"""
    try:
        task = Task.query.get_or_404(task_id)
        
        result = task.to_dict()
        
        # 如果任务已完成且有结果文件，读取结果
        if task.status == 'completed' and task.result_file_path and os.path.exists(task.result_file_path):
            try:
                with open(task.result_file_path, 'r') as f:
                    task_results = json.load(f)
                result['task_results'] = task_results
            except:
                pass
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/tasks/<int:task_id>/cancel', methods=['POST'])
@cross_origin()
def cancel_task(task_id):
    """取消任务"""
    try:
        task = Task.query.get_or_404(task_id)
        
        if task.status not in ['pending', 'running']:
            return jsonify({'error': '只能取消待执行或正在执行的任务'}), 400
        
        # 更新任务状态
        task.status = 'cancelled'
        task.completed_at = datetime.utcnow()
        db.session.commit()
        
        # TODO: 取消Celery任务
        
        return jsonify({'message': '任务已取消'})
        
    except Exception as e:
        logger.error(f"取消任务失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/models', methods=['GET'])
@cross_origin()
def get_models():
    """获取模型列表"""
    try:
        models = Model.query.filter(Model.is_active == True).order_by(Model.created_at.desc()).all()
        return jsonify({
            'models': [model.to_dict() for model in models]
        })
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/models/<int:model_id>', methods=['GET'])
@cross_origin()
def get_model(model_id):
    """获取模型详情"""
    try:
        model = Model.query.get_or_404(model_id)
        return jsonify(model.to_dict())
    except Exception as e:
        logger.error(f"获取模型详情失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/models/<int:model_id>', methods=['DELETE'])
@cross_origin()
def delete_model(model_id):
    """删除模型"""
    try:
        model = Model.query.get_or_404(model_id)
        
        # 软删除 - 设置为非活跃状态
        model.is_active = False
        db.session.commit()
        
        return jsonify({'message': '模型已删除'})
        
    except Exception as e:
        logger.error(f"删除模型失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/compare', methods=['POST'])
@cross_origin()
def start_model_comparison():
    """开始模型比较任务"""
    try:
        data = request.get_json()
        
        required_fields = ['qwen_model_id', 'lstm_model_id', 'test_dataset_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        qwen_model_id = data['qwen_model_id']
        lstm_model_id = data['lstm_model_id']
        test_dataset_id = data['test_dataset_id']
        
        # 验证模型和数据集存在
        qwen_model = Model.query.get(qwen_model_id)
        lstm_model = Model.query.get(lstm_model_id)
        test_dataset = Dataset.query.get(test_dataset_id)
        
        if not qwen_model or not lstm_model or not test_dataset:
            return jsonify({'error': '模型或数据集不存在'}), 404
        
        # 创建比较任务
        task = Task(
            task_type='comparison',
            data_type=qwen_model.data_type,
            model_type='comparison',
            parameters=json.dumps({
                'qwen_model_id': qwen_model_id,
                'lstm_model_id': lstm_model_id,
                'test_dataset_id': test_dataset_id
            })
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 启动比较任务
        model_comparison_task.delay(
            task_id=task.id,
            qwen_model_id=qwen_model_id,
            lstm_model_id=lstm_model_id,
            test_data_path=test_dataset.file_path
        )
        
        logger.info(f"模型比较任务已启动: {task.id}")
        
        return jsonify({
            'message': '模型比较任务已启动',
            'task_id': task.id,
            'status': task.status
        })
        
    except Exception as e:
        logger.error(f"启动模型比较任务失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/sample-data', methods=['POST'])
@cross_origin()
def generate_sample_data():
    """生成示例数据"""
    try:
        data = request.get_json()
        data_type = data.get('data_type', 'weather')
        num_samples = data.get('num_samples', 1000)
        
        if data_type not in Config.SUPPORTED_TASKS:
            return jsonify({'error': f'不支持的数据类型: {data_type}'}), 400
        
        # 生成示例数据
        processor = TimeSeriesProcessor()
        
        # 创建保存路径
        sample_dir = os.path.join(Config.UPLOAD_FOLDER, 'samples')
        os.makedirs(sample_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"sample_{data_type}_{timestamp}.csv"
        file_path = os.path.join(sample_dir, filename)
        
        df = processor.generate_sample_data(
            data_type=data_type,
            num_samples=num_samples,
            save_path=file_path
        )
        
        # 创建数据集记录
        dataset = Dataset(
            name=f"示例{data_type}数据",
            data_type=data_type,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            num_samples=len(df),
            num_features=len(df.columns)
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        return jsonify({
            'message': '示例数据生成成功',
            'dataset_id': dataset.id,
            'file_path': file_path,
            'preview': df.head(10).to_dict('records')
        })
        
    except Exception as e:
        logger.error(f"生成示例数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/download/<int:task_id>/results', methods=['GET'])
@cross_origin()
def download_results(task_id):
    """下载任务结果"""
    try:
        task = Task.query.get_or_404(task_id)
        
        if not task.result_file_path or not os.path.exists(task.result_file_path):
            return jsonify({'error': '结果文件不存在'}), 404
        
        return send_file(
            task.result_file_path,
            as_attachment=True,
            download_name=f"task_{task_id}_results.json"
        )
        
    except Exception as e:
        logger.error(f"下载结果失败: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """获取系统统计信息"""
    try:
        stats = {
            'total_tasks': Task.query.count(),
            'completed_tasks': Task.query.filter(Task.status == 'completed').count(),
            'running_tasks': Task.query.filter(Task.status == 'running').count(),
            'failed_tasks': Task.query.filter(Task.status == 'failed').count(),
            'total_models': Model.query.filter(Model.is_active == True).count(),
            'total_datasets': Dataset.query.count(),
            'qwen_models': Model.query.filter(Model.model_type == 'qwen', Model.is_active == True).count(),
            'lstm_models': Model.query.filter(Model.model_type == 'lstm', Model.is_active == True).count()
        }
        
        # 最近的任务
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
        stats['recent_tasks'] = [task.to_dict() for task in recent_tasks]
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'error': str(e)}), 500
