# worker.py
import threading
import time
import subprocess
from jobs import fetch_pending_job, update_job_state, increment_attempts, move_to_dlq
from config import get_config

workers = []
stop_event = threading.Event()

# Handle failed jobs with retry logic
def handle_failure(job):
    increment_attempts(job['id'])
    # fetch latest attempts
    jobs = [j for j in [job] if j]  # fallback in case job is None
    attempts = job['attempts'] + 1  # incremented in DB
    max_retries = job.get('max_retries', get_config('max_retries'))
    backoff_base = get_config('backoff_base')

    if attempts <= max_retries:
        delay = backoff_base ** attempts
        print(f"[Retry] Job {job['id']} failed. Retrying in {delay}s (attempt {attempts})")
        for _ in range(delay):
            if stop_event.is_set():
                return
            time.sleep(1)
        update_job_state(job['id'], 'pending')
    else:
        print(f"[DLQ] Job {job['id']} exceeded retries. Moving to DLQ")
        move_to_dlq(job['id'])

# Execute the job command
def execute_job(worker_id, job):
    print(f"[Worker {worker_id}] Executing job {job['id']}: {job['command']}")
    try:
        result = subprocess.run(job['command'], shell=True)
        if stop_event.is_set():
            print(f"[Worker {worker_id}] Interrupted. Stopping job {job['id']}")
            update_job_state(job['id'], 'pending')
            return
        if result.returncode == 0:
            update_job_state(job['id'], 'completed')
            print(f"[Worker {worker_id}] Job {job['id']} completed successfully")
        else:
            handle_failure(job)
    except Exception as e:
        print(f"[Worker {worker_id}] Exception: {e}")
        handle_failure(job)

# Worker loop to continuously fetch and execute jobs
def worker_loop(worker_id):
    while not stop_event.is_set():
        job = fetch_pending_job()
        if job:
            execute_job(worker_id, job)
        else:
            time.sleep(0.2)  # avoid busy wait

# Start N workers
def start_workers(count):
    try:
        for i in range(count):
            t = threading.Thread(target=worker_loop, args=(i+1,), daemon=True)
            workers.append(t)
            t.start()
        print(f"{count} worker(s) started. Press Ctrl+C to stop.")
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Stopping workers...")
        stop_workers()

# Stop all workers
def stop_workers():
    stop_event.set()
    print("Stopping workers...")
    for t in workers:
        t.join()
    print("All workers stopped.")
