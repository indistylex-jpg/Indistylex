from app import create_app

app = create_app()

# Celery setup (optional for dev server, required for async tasks)
celery = None
try:
    from celery import Celery

    def make_celery(app):
        c = Celery(
            app.import_name,
            broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
            backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        )
        c.conf.update(app.config)

        class ContextTask(c.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        c.Task = ContextTask
        return c

    celery = make_celery(app)
except ImportError:
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
