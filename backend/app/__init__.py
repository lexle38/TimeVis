from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import os
from loguru import logger

from config.config import config
from app.models import db
from app.routes import api

def create_app(config_name=None):
    """创建Flask应用"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    migrate = Migrate(app, db)
    
    # 注册蓝图
    app.register_blueprint(api)
    
    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 配置日志
    logger.add(
        "logs/timevis.log",
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    logger.info("Flask应用创建成功")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
