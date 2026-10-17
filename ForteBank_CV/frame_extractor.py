import cv2
from pathlib import Path
from video_processor import get_video_info

def extract_frames(video_path, output_dir, interval_sec=1.0):
    if interval_sec <= 0:
        raise ValueError('interval_sec must be positive')
    info = get_video_info(video_path)
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    written = []
    frame_index, next_sec = 0, 0.0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            sec = frame_index / info['fps']
            if sec + 1e-8 >= next_sec:
                dest = folder / f'frame_{frame_index:07d}_{sec:.3f}s.jpg'
                if not cv2.imwrite(str(dest), frame):
                    raise IOError(f'Cannot write {dest}')
                written.append(str(dest))
                next_sec += interval_sec
            frame_index += 1
    finally:
        cap.release()
    return written
