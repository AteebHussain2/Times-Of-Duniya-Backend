from rq import Worker, Queue
from redis import Redis
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Connect to Redis inside Docker (service name)
redis_conn = Redis(host='redis', port=6379)

# Start RQ worker
queue = Queue(connection=redis_conn)
worker = Worker([queue], connection=redis_conn)
worker.work()
