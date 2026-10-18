
from fastapi import (
    FastAPI, UploadFile, File,
    HTTPException, Security
)
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from pathlib import Path

from database import (
    init_db,
    save_job,
    get_job_from_db
)
from video_validator import validate_video
from worker import (
    start_worker,
    stop_worker,
    add_video_to_queue
)

import os
import uuid
import hmac


# Запуск и остановка обработчика
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_worker()

    yield

    stop_worker()


app = FastAPI(
    title="ForteBank AI Backend",
    lifespan=lifespan
)


# API-ключ
api_key_header = APIKeyHeader(name="X-API-Key")
API_KEY = os.getenv("FORTEBANK_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "FORTEBANK_API_KEY is not configured"
    )


def verify_api_key(
    api_key: str = Security(api_key_header)
):
    if not hmac.compare_digest(api_key, API_KEY):
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )


# Папка загрузок
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_SIZE = 200 * 1024 * 1024


@app.get("/")
def home():
    return {
        "message": "ForteBank Backend is working!"
    }


# API 1: Загрузка видео
@app.post(
    "/api/v1/analyze",
    dependencies=[Security(verify_api_key)]
)
def analyze_video(file: UploadFile = File(...)):

    if (
        not file.filename
        or not file.filename.lower().endswith(".mov")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only .mov files are allowed"
        )

    job_id = str(uuid.uuid4())

    video_path = UPLOAD_DIR / f"{job_id}.mov"

    # Сохраняем файл частями
    total_size = 0

    try:
        with open(video_path, "wb") as buffer:
            while True:
                chunk = file.file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Video exceeds 200 MB"
                    )

                buffer.write(chunk)

        # Проверяем видео
        validate_video(str(video_path))

    except HTTPException:
        video_path.unlink(missing_ok=True)
        raise

    except ValueError as error:
        video_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        video_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Video upload failed"
        )

    finally:
        file.file.close()

    # Сохраняем задачу
    save_job(job_id, "processing")

    # Передаём видео в очередь
    add_video_to_queue(
        job_id,
        str(video_path)
    )

    return {
        "job_id": job_id,
        "status": "processing"
    }


# API 2: Результаты
@app.get(
    "/api/v1/jobs/{job_id}",
    dependencies=[Security(verify_api_key)]
)
def get_job(job_id: str):

    job = get_job_from_db(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job
