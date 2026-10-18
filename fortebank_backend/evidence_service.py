
import cv2
import base64


def extract_evidence(video_path: str, time_sec: float):
    """
    Извлекает JPEG-кадр из видео
    на указанной секунде.
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Cannot open video")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps <= 0 or frame_count <= 0:
            raise ValueError("Invalid video metadata")

        duration = frame_count / fps

        if not 0 <= time_sec < duration:
            raise ValueError("Timestamp outside video")

        cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)

        success, frame = cap.read()

        if not success:
            raise ValueError("Cannot extract frame")

        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 85]
        )

        if not success:
            raise ValueError("Cannot encode JPEG")

        encoded = base64.b64encode(
            buffer.tobytes()
        ).decode("utf-8")

        actual_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

        return {
            "timestamp_sec": round(
                actual_sec if actual_sec > 0 else time_sec, 3
            ),
            "image_base64": encoded
        }

    finally:
        cap.release()
