web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
worker: celery -A app.tasks.tasks.celery_app worker --loglevel=info -Q ai,notifications,scoring,reports -c 2
beat: celery -A app.tasks.tasks.celery_app beat --loglevel=info
