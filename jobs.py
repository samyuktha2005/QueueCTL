# jobs.py
from tinydb import TinyDB, Query
from datetime import datetime
import uuid

# DB setup
db = TinyDB('jobs.json')
JobTable = db.table('jobs')
DLQTable = db.table('dlq')

# Create a new job
def create_job(command, max_retries=3):
    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    job = {
        "id": job_id,
        "command": command,
        "state": "pending",
        "attempts": 0,
        "max_retries": max_retries,
        "created_at": now,
        "updated_at": now
    }
    return job

# Add job to DB
def add_job(job):
    JobTable.insert(job)

# Update job state
def update_job_state(job_id, new_state):
    now = datetime.utcnow().isoformat()
    JobTable.update({'state': new_state, 'updated_at': now}, Query().id == job_id)


# Increment attempts
def increment_attempts(job_id):
    job = JobTable.get(Query().id == job_id)
    if job:
        attempts = job['attempts'] + 1
        JobTable.update({'attempts': attempts, 'updated_at': datetime.utcnow().isoformat()}, Query().id == job_id)

# Get jobs by state
def get_jobs(state=None):
    if state:
        return JobTable.search(Query().state == state)
    return JobTable.all()

# Move job to Dead Letter Queue
def move_to_dlq(job_id):
    job = JobTable.get(Query().id == job_id)
    if job:
        job['state'] = 'dead'
        job['updated_at'] = datetime.utcnow().isoformat()
        DLQTable.insert(job)
        JobTable.remove(Query().id == job_id)

# DLQ operations
def get_dlq_jobs():
    return DLQTable.all()

def retry_dlq_job(job_id):
    job = DLQTable.get(Query().id == job_id)
    if job:
        job['state'] = 'pending'
        job['attempts'] = 0
        job['updated_at'] = datetime.utcnow().isoformat()
        JobTable.insert(job)
        DLQTable.remove(Query().id == job_id)
