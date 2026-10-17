
import queue
import threading

from ai_service import analyze_video_ai
from database import save_job, get_unfinished_jobs
from pathlib import Path


# Очередь видео
video_queue = queue.Queue()

# Сигнал остановки
stop_event = threading.Event()

worker_thread = None


def process_queue():
    print("Video worker started")

    while not stop_event.is_set():
        try:
            job_id, video_path = video_queue.get(
                timeout=1
            )
        except queue.Empty:
            continue

        try:
            print(f"Processing video: {job_id}")

            result = analyze_video_ai(video_path)

            save_job(
                job_id,
                "done",
                result
            )

            print(f"Video completed: {job_id}")

        except Exception as error:
            print(f"Processing failed: {error}")

            save_job(
                job_id,
                "failed",
                {"error": "Video processing failed"}
            )

        finally:
            video_queue.task_done()



def start_worker():
    global worker_thread

    stop_event.clear()

    worker_thread = threading.Thread(
        target=process_queue,
        daemon=True
    )

    worker_thread.start()

    # Восстанавливаем незавершённые задачи
    unfinished_jobs = get_unfinished_jobs()

    for job_id in unfinished_jobs:
        video_path = Path("uploads") / f"{job_id}.mov"

        if video_path.exists():
            video_queue.put((job_id, str(video_path)))
            print(f"Recovered job: {job_id}")
        else:
            save_job(
                job_id,
                "failed",
                {"error": "Video file not found"}
            )



def stop_worker():
    stop_event.set()

    if worker_thread is not None:
        worker_thread.join(timeout=2)


def add_video_to_queue(job_id, video_path):
    video_queue.put((job_id, video_path))

    print(f"Video added to queue: {job_id}")
