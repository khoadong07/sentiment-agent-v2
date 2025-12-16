# Gunicorn configuration for production
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes - tối ưu cho high load
workers = int(os.getenv('WORKERS', min(multiprocessing.cpu_count() * 2, 8)))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 2000
max_requests = 2000
max_requests_jitter = 100

# Timeouts - tối ưu cho production
timeout = 45
keepalive = 10
graceful_timeout = 45

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'sentiment-analysis-api'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Performance tuning
preload_app = True
enable_stdio_inheritance = True

def when_ready(server):
    server.log.info("Sentiment Analysis API ready to serve requests")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)