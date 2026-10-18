
from pathlib import Path
import cv2

# Для начала ограничим размер видео 200 МБ.
MAX_FILE_SIZE = 200 * 1024 * 1024

# Максимальная длительность — 150 секунд.
MAX_DURATION = 150


def validate_video(video_path: str):
    path = Path(video_path)

    if not path.exists():
        raise ValueError("Video file not found")

    if path.stat().st_size == 0:
        raise ValueError("Video file is empty")

    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("Video exceeds 200 MB")

    cap = cv2.VideoCapture(str(path))

    try:
        if not cap.isOpened():
            raise ValueError("Cannot open video")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps <= 0 or frames <= 0:
            raise ValueError("Invalid video metadata")

        duration = frames / fps

        if duration > MAX_DURATION:
            raise ValueError("Video is too long")

        # Проверка возможности декодировать кадр
        success, _ = cap.read()

        if not success:
            raise ValueError("Cannot decode video")

        return {
            "duration_sec": round(duration, 2),
            "fps": round(fps, 2),
            "frame_count": int(frames)
        }

    finally:
        cap.release()
