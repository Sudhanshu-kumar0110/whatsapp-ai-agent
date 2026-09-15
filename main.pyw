import subprocess
import sys
import os
import time
import win32api
import win32con
import win32job

project_dir = os.path.dirname(os.path.abspath(__file__))

go_dir = os.path.join(
    project_dir,
    "whatsapp-mcp",
    "whatsapp-bridge"
)


# =========================
# Create Windows Job Object
# =========================

job = win32job.CreateJobObject(None, "")

info = win32job.QueryInformationJobObject(
    job,
    win32job.JobObjectExtendedLimitInformation
)

info["BasicLimitInformation"]["LimitFlags"] = (
    win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
)

win32job.SetInformationJobObject(
    job,
    win32job.JobObjectExtendedLimitInformation,
    info
)


processes = []


def start_process(command, cwd):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    # Put process inside Job Object
    win32job.AssignProcessToJobObject(
        job,
        win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS,
            False,
            process.pid
        )
    )

    processes.append(process)

    return process


# =========================
# Go WhatsApp Bridge
# =========================

start_process(
    ["cmd.exe", "/c", "go run main.go"],
    go_dir
)

time.sleep(10)


# =========================
# RQ Worker
# =========================

rq_worker = os.path.join(
    project_dir,
    "run_rq_worker.py"
)

start_process(
    [sys.executable, rq_worker],
    project_dir
)


# =========================
# FastAPI
# =========================

start_process(
    [
        sys.executable,
        "-c",
        "from whatsapp_agent.agent_api import main; main()"
    ],
    project_dir
)


print("================================")
print(" WhatsApp AI Agent Started")
print("================================")
print("Go Bridge  : Running")
print("RQ Worker  : Running")
print("FastAPI    : Running")
print()
print("Close this terminal to stop EVERYTHING.")


# Keep main.py alive
while True:
    time.sleep(1)