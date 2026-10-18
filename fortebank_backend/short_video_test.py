
import cv2
from pathlib import Path

source = Path("test_videos/sample.mov")
output = Path("test_videos/short.mov")

cap = cv2.VideoCapture(str(source))

if not cap.isOpened():
    raise RuntimeError("Cannot open source video")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

if fps <= 0 or width <= 0 or height <= 0:
    cap.release()
    raise RuntimeError("Invalid video metadata")

writer = cv2.VideoWriter(
    str(output),
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height),
)

if not writer.isOpened():
    cap.release()
    raise RuntimeError("Cannot create short video")

count = 0
max_frames = max(1, int(fps * 0.8))

while count < max_frames:
    ok, frame = cap.read()

    if not ok:
        break

    writer.write(frame)
    count += 1

cap.release()
writer.release()

print("Short video created")
print("Frames:", count)
print("Output:", output)
