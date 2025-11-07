# worker.py
import threading
import time
import subprocess
from jobs import get_jobs, update_job_state, increment_attempts, move_to_dlq
from config import get_config

workers = []
stop_event = threading.Event()

def worker_loop(worker_id):
    while not stop_event.is_set():
        jobs = get_jobs(state="pending")
        if not jobs:
            time.sleep(1)
            continue
        job = jobs[0]
        update_job_state(job["id"], "processing")
        print(f"[Worker {worker_id}] Executing job {job['id']}: {job['command']}")
        try:
            result = subprocess.run(job["command"], shell=True)
            if result.returncode == 0:
                update_job_state(job["id"], "completed")
                print(f"[Worker {worker_id}] Job {job['id']} completed successfully")
            else:
                handle_failure(job)
        except Exception as e:
            handle_failure(job)

def handle_failure(job):
    increment_attempts(job["id"])
    attempts = job["attempts"] + 1
    max_retries = job.get("max_retries", get_config("max_retries"))
    backoff_base = get_config("backoff_base")
    if attempts <= max_retries:
        delay = backoff_base ** attempts
        print(f"[Retry] Job {job['id']} failed. Retrying in {delay} sec (attempt {attempts})")
        time.sleep(delay)
        update_job_state(job["id"], "pending")
    else:
        print(f"[DLQ] Job {job['id']} exceeded retries. Moving to DLQ")
        move_to_dlq(job["id"])

def start_workers(count):
    for i in range(count):
        t = threading.Thread(target=worker_loop, args=(i+1,), daemon=True)
        workers.append(t)
        t.start()
    print(f"{count} worker(s) started.")

def stop_workers():
    stop_event.set()
    print("Stopping workers...")
    for t in workers:
        t.join()
    print("All workers stopped.")
