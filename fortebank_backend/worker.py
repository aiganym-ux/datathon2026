
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from database import save_job, get_unfinished_jobs


video_queue = queue.Queue()
stop_event = threading.Event()
worker_thread = None

TIMEOUT_SECONDS = 300

UPLOAD_DIR = Path("uploads")
EVIDENCE_DIR = Path("runtime_evidence")


def process_video(job_id, video_path):
    result_path = UPLOAD_DIR / f"{job_id}.result.json"

    try:
        print(f"Processing video: {job_id}", flush=True)

        subprocess.run(
            [
                sys.executable,
                "job_runner.py",
                str(video_path),
                str(result_path),
            ],
            check=True,
            timeout=TIMEOUT_SECONDS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

        if not result_path.is_file():
            raise RuntimeError("AI result file not created")

        with result_path.open("r", encoding="utf-8") as file:
            result = json.load(file)

        if not isinstance(result, dict):
            raise ValueError("AI result must be a dictionary")

        save_job(job_id, "done", result)

        print(f"Video completed: {job_id}", flush=True)

    except subprocess.TimeoutExpired:
        save_job(
            job_id,
            "failed",
            {"error": "Video analysis exceeded 300 seconds"},
        )
        print(f"Video timeout: {job_id}", flush=True)

    except Exception as error:
        # Do not log video content or Base64 evidence.
        print(
            f"Video processing failed: {type(error).__name__}",
            flush=True,
        )
        save_job(
            job_id,
            "failed",
            {"error": "Video processing failed"},
        )

    finally:
        # Remove temporary files, but keep results in SQLite.
        result_path.unlink(missing_ok=True)
        Path(video_path).unlink(missing_ok=True)

        # Evidence JPEGs are temporary. Base64 is kept in the
        # completed job result in SQLite.
        if EVIDENCE_DIR.exists():
            shutil.rmtree(EVIDENCE_DIR, ignore_errors=True)


def process_queue():
    print("Video worker started", flush=True)

    while not stop_event.is_set():
        try:
            job_id, video_path = video_queue.get(timeout=1)
        except queue.Empty:
            continue

        try:
            process_video(job_id, video_path)
        finally:
            video_queue.task_done()


def start_worker():
    global worker_thread

    stop_event.clear()

    worker_thread = threading.Thread(
        target=process_queue,
        daemon=True,
    )
    worker_thread.start()

    # Recover jobs interrupted by a previous container restart.
    for job_id in get_unfinished_jobs():
        video_path = UPLOAD_DIR / f"{job_id}.mov"

        if video_path.is_file():
            video_queue.put((job_id, str(video_path)))
            print(f"Recovered job: {job_id}", flush=True)
        else:
            save_job(
                job_id,
                "failed",
                {"error": "Video file not found"},
            )


def stop_worker():
    stop_event.set()

    if worker_thread is not None:
        worker_thread.join(timeout=2)


def add_video_to_queue(job_id, video_path):
    video_queue.put((job_id, video_path))
    print(f"Video added to queue: {job_id}", flush=True)
