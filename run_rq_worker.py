import os
import subprocess

project_dir = os.path.dirname(os.path.abspath(__file__))

rq_exe = os.path.join(
    project_dir,
    ".venv",
    "Scripts",
    "rq.exe"
)

subprocess.run([
    rq_exe,
    "worker",
    "--worker-class",
    "rq.worker.SimpleWorker",
    "default"
])

input("RQ worker stopped. Press Enter to close...")