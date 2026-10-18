import base64
from pathlib import Path
import cv2
from video_processor import get_video_info

def evidence_at(video_path, time_sec, output_dir='evidence'):
    info = get_video_info(video_path)
    if time_sec < 0 or time_sec >= info['duration_sec']:
        raise ValueError(f'Time {time_sec} is outside video duration {info["duration_sec"]:.2f}s')
    # Sequential decoding from a nearby keyframe can improve precision for variable codecs.
    cap = cv2.VideoCapture(str(video_path))
    try:
        cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError('Cannot decode evidence frame')
        # Backend-dependent; approximate actual timestamp by frame index if needed.
        actual_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        actual_sec = actual_ms / 1000 if actual_ms > 0 else time_sec
    finally:
        cap.release()
    ok, encoded = cv2.imencode('.jpg', frame)
    if not ok:
        raise RuntimeError('JPEG encoding failed')
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    filename = folder / f'{Path(video_path).stem}_{time_sec:.3f}s.jpg'
    filename.write_bytes(encoded.tobytes())
    return {'timestamp_sec': round(actual_sec, 3), 'image_base64': base64.b64encode(encoded.tobytes()).decode('ascii')}

def evidence_for_event(video_path, time_sec, offsets=(-0.3, 0.0, 0.3), output_dir='evidence'):
    duration = get_video_info(video_path)['duration_sec']
    times = sorted({round(time_sec + o, 3) for o in offsets if 0 <= time_sec + o < duration})
    return [evidence_at(video_path, t, output_dir=output_dir) for t in times[:3]]
