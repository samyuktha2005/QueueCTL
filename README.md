🚀 QueueCTL — CLI-Based Job Queue System

A lightweight background job queue system built using Python, supporting multiple workers, persistent storage, retries with exponential backoff, and a Dead Letter Queue (DLQ).

⚙️ Features

✅ Enqueue and process background jobs
✅ Multiple worker threads
✅ Persistent storage via TinyDB
✅ Automatic retry with exponential backoff
✅ Dead Letter Queue for failed jobs
✅ Configurable max retries and backoff base
✅ Graceful worker shutdown
✅ Cross-platform command execution (Windows compatible)

🧠 Architecture Overview
Job Lifecycle
State	Description
pending	Job is waiting to be picked up by a worker
processing	Worker is executing the job
completed	Successfully executed
failed	Retryable failure occurred
dead	Moved to DLQ after max retries
Components
File	Purpose
queuectl.py	CLI interface using click
jobs.py	Job model, persistence, CRUD
worker.py	Worker thread logic, retries, DLQ handling
config.py	Config management for retries/backoff
jobs.json	Persistent TinyDB storage
🧩 Setup Instructions
Prerequisites

Python 3.8 or later

pip install tinydb click

Clone the Repository
git clone https://github.com/Samyuktha2005/QueueCTL.git
cd QueueCTL

Install Dependencies
pip install -r requirements.txt


💻 Usage Examples
1️⃣ Enqueue a Job
python queuectl.py --% enqueue "{\"command\": \"timeout /t 5\"}"


(Windows)

or on Linux/macOS:

python queuectl.py enqueue "{\"command\": \"sleep 5\"}"

2️⃣ Start Workers
python queuectl.py worker start --count 2


Starts 2 worker threads to process jobs concurrently.

3️⃣ Check Status
python queuectl.py status


Shows summary of jobs by state (pending, completed, etc.)

4️⃣ List Jobs
python queuectl.py list --state completed

5️⃣ View DLQ
python queuectl.py dlq list

6️⃣ Retry a DLQ Job
python queuectl.py dlq retry <job_id>

7️⃣ Stop Workers

Press Ctrl+C or use:

python queuectl.py worker stop

🧪 Testing Instructions (for 10% marks)

Use the following scenarios to validate all requirements.

✅ Scenario 1: Basic Job Success
python queuectl.py enqueue "{\"command\": \"timeout /t 3\"}"
python queuectl.py worker start --count 1


Expected:
Job transitions: pending → processing → completed

✅ Scenario 2: Failed Job Retries and DLQ
python queuectl.py --% enqueue "{\"command\": \"invalidcmd\"}"
python queuectl.py worker start --count 1


Expected:

Job fails → retries with exponential backoff (2s, 4s, 8s, …)

After max retries → moved to DLQ

✅ Scenario 3: Multiple Workers (Parallel Execution)
python queuectl.py enqueue "{\"command\": \"timeout /t 5\"}"
python queuectl.py enqueue "{\"command\": \"timeout /t 5\"}"
python queuectl.py worker start --count 2


Expected:
Both jobs run in parallel on different workers.

✅ Scenario 4: Persistence

Enqueue jobs.

Stop program (Ctrl+C).

Restart workers with:

python queuectl.py worker start --count 1


Expected:
Pending jobs are picked up and completed. No jobs lost between restarts.

✅ Scenario 5: Invalid Command Handling
python queuectl.py enqueue "{\"command\": \"foobar123\"}"
python queuectl.py worker start --count 1


Expected:
Job fails gracefully → retries → DLQ.

📊 Configuration
Config	Description	Default
max_retries	Max number of attempts before DLQ	3
backoff_base	Base for exponential delay (2^attempts)	2
Update Config
python queuectl.py config set max_retries 5
python queuectl.py config set backoff_base 3

🧱 Assumptions & Trade-offs

Only one worker thread executes a single job at a time (no overlap).

Jobs execute shell commands (no sandboxing for now).

TinyDB provides persistence without external DB.

Workers perform graceful shutdowns (finish current job before stopping).

🧠 Bonus Ideas

Add job scheduling with run_at

Add priority queues

Add job output logging to file

Add simple monitoring dashboard (Flask UI)

🧾 Author

Samyuktha Jaggaiahgari
Python Developer — QueueCTL CLI System