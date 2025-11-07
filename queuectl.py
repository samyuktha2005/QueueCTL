# queuectl.py
import click
from jobs import create_job, add_job, get_jobs, get_dlq_jobs, retry_dlq_job
from worker import start_workers, stop_workers
from config import set_config, get_config

@click.group()
def cli():
    """QueueCTL - CLI job queue manager"""
    pass

# Enqueue
@cli.command()
@click.argument("job_json")
def enqueue(job_json):
    import json
    job_data = json.loads(job_json)
    command = job_data.get("command")
    max_retries = job_data.get("max_retries", get_config("max_retries"))
    job = create_job(command, max_retries=max_retries)
    add_job(job)
    click.echo(f"Job {job['id']} enqueued.")

# Start workers
@cli.group()
def worker():
    pass

@worker.command("start")
@click.option("--count", default=1, help="Number of workers to start")
def start(count):
    start_workers(count)

@worker.command("stop")
def stop():
    stop_workers()

# Status
@cli.command()
def status():
    jobs = get_jobs()
    states = {}
    for j in jobs:
        states[j["state"]] = states.get(j["state"], 0) + 1
    click.echo("Job States Summary:")
    for state, count in states.items():
        click.echo(f"{state}: {count}")

# List jobs
@cli.command()
@click.option("--state", default=None, help="Filter jobs by state")
def list(state):
    jobs = get_jobs(state)
    for j in jobs:
        click.echo(f"{j['id']} - {j['command']} - {j['state']} - attempts: {j['attempts']}")

# DLQ commands
@cli.group()
def dlq():
    pass

@dlq.command("list")
def dlq_list():
    jobs = get_dlq_jobs()
    for j in jobs:
        click.echo(f"{j['id']} - {j['command']} - state: {j['state']}")

@dlq.command("retry")
@click.argument("job_id")
def dlq_retry(job_id):
    retry_dlq_job(job_id)
    click.echo(f"Job {job_id} moved back to pending.")

# Config
@cli.group()
def config():
    pass

@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    if value.isdigit():
        value = int(value)
    set_config(key, value)
    click.echo(f"Config {key} set to {value}")

if __name__ == "__main__":
    cli()
