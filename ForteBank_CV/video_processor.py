import cv2
from pathlib import Path

def get_video_info(path):
    if not Path(path).is_file():
        raise FileNotFoundError(path)
    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            raise ValueError(f'Cannot decode video: {path}')
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if fps <= 0:
            raise ValueError('Invalid FPS')
        return {'fps': fps, 'frame_count': frames, 'duration_sec': frames / fps}
    finally:
        cap.release()
