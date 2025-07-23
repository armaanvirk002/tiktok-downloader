# Gunicorn configuration for Render deployment
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WORKERS', 2))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Restart workers after this many requests, to help control memory usage
max_requests = 1000
max_requests_jitter = 100

# Preload the application before forking worker processes
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'tiktok-downloader'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Application
module = "app:app"

# Enable automatic worker restarts
reload = os.environ.get('RELOAD', 'False').lower() == 'true'

# Graceful timeout
graceful_timeout = 30

# Environment variables
raw_env = [
    f"PORT={os.environ.get('PORT', 5000)}",
    f"SESSION_SECRET={os.environ.get('SESSION_SECRET', 'change-me-in-production')}",
]

def when_ready(server):
    """Callback when server is ready"""
    server.log.info("TikTok Downloader server is ready. Listening on %s", server.address)

def worker_int(worker):
    """Callback when worker receives INT signal"""
    worker.log.info("Worker received INT signal")

def pre_fork(server, worker):
    """Callback before worker fork"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Callback after worker fork"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Callback after worker initialization"""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Callback when worker is aborted"""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
