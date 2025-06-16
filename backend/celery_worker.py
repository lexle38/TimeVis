import os
from celery import Celery
from app import create_app
from app.tasks import celery

def make_celery(app):
    """创建Celery实例"""
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        """继承任务类以获取应用上下文"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# 创建Flask应用和Celery实例
flask_app = create_app()
celery_app = make_celery(flask_app)

if __name__ == '__main__':
    celery_app.start()
