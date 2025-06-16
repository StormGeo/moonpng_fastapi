# gunicorn_config.py

import multiprocessing

# App: main.py com objeto `app`
bind = "0.0.0.0:8000"

# Número de workers (processos)
workers = 4  # ou: multiprocessing.cpu_count()

# Tipo de worker para FastAPI (ASGI)
worker_class = "uvicorn.workers.UvicornWorker"

# Tempo máximo de resposta (em segundos)
timeout = 90

# Limita o número de requisições por worker antes de reiniciar (previne leaks)
max_requests = 1000
max_requests_jitter = 50

# Nível de log
loglevel = "info"
accesslog = "-"  # log no stdout
errorlog = "-"  # log no stderr

# Nome do processo (aparece no top/htop)
proc_name = "moonpng-api"

# Recomendado se você usa root_path ou reverse proxy
# root_path = "/api"
