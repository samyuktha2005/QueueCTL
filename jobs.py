# jobs.py
from tinydb import TinyDB, Query
from datetime import datetime
import uuid
import threading

# DB setup
DB_PATH = 'jobs.json'
db_lock = threading.Lock()  # global lock for thread-safe DB access

def get_db():
    return TinyDB(DB_PATH)

# Create a new job
def create_job(command, max_retries=3):
    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    return {
        "id": job_id,
        "command": command,
        "state": "pending",
        "attempts": 0,
        "max_retries": max_retries,
        "created_at": now,
        "updated_at": now
    }

# Add job to DB
def add_job(job):
    with db_lock:
        db = get_db()
        table = db.table('jobs')
        table.insert(job)
        db.close()

# Atomically update job state
def update_job_state(job_id, new_state):
    now = datetime.utcnow().isoformat()
    with db_lock:
        db = get_db()
        table = db.table('jobs')
        table.update({'state': new_state, 'updated_at': now}, Query().id == job_id)
        db.close()

# Increment attempts
def increment_attempts(job_id):
    with db_lock:
        db = get_db()
        table = db.table('jobs')
        job = table.get(Query().id == job_id)
        if job:
            attempts = job['attempts'] + 1
            table.update({'attempts': attempts, 'updated_at': datetime.utcnow().isoformat()}, Query().id == job_id)
        db.close()

# Atomically fetch one pending job and mark as processing
def fetch_pending_job():
    with db_lock:
        db = get_db()
        table = db.table('jobs')
        jobs = table.search(Query().state == "pending")
        if not jobs:
            db.close()
            return None
        job = jobs[0]
        table.update({'state': 'processing', 'updated_at': datetime.utcnow().isoformat()}, Query().id == job['id'])
        db.close()
        return job

# Get all jobs or by state
def get_jobs(state=None):
    with db_lock:
        db = get_db()
        table = db.table('jobs')
        if state:
            result = table.search(Query().state == state)
        else:
            result = table.all()
        db.close()
        return result

# Move job to Dead Letter Queue
def move_to_dlq(job_id):
    with db_lock:
        db = get_db()
        jobs_table = db.table('jobs')
        dlq_table = db.table('dlq')
        job = jobs_table.get(Query().id == job_id)
        if job:
            job['state'] = 'dead'
            job['updated_at'] = datetime.utcnow().isoformat()
            dlq_table.insert(job)
            jobs_table.remove(Query().id == job_id)
        db.close()

# DLQ operations
def get_dlq_jobs():
    with db_lock:
        db = get_db()
        dlq_table = db.table('dlq')
        result = dlq_table.all()
        db.close()
        return result

def retry_dlq_job(job_id):
    with db_lock:
        db = get_db()
        jobs_table = db.table('jobs')
        dlq_table = db.table('dlq')
        job = dlq_table.get(Query().id == job_id)
        if job:
            job['state'] = 'pending'
            job['attempts'] = 0
            job['updated_at'] = datetime.utcnow().isoformat()
            jobs_table.insert(job)
            dlq_table.remove(Query().id == job_id)
        db.close()
