
import base64
import sys
from pathlib import Path

from ml_pipeline import analyze_video
from ForteBank_CV.video_processor import get_video_info


def main():
    if len(sys.argv) != 2:
        print("Usage: python cv_test.py path_to_video.mov")
        sys.exit(1)

    video_path = Path(sys.argv[1]).resolve()

    if not video_path.is_file():
        print("ERROR: Video file not found")
        sys.exit(1)

    info = get_video_info(video_path)

    print("Video duration:", round(info["duration_sec"], 2))
    print("FPS:", round(info["fps"], 2))
    print("Total frames:", info["frame_count"])

    if info["duration_sec"] <= 0:
        raise ValueError("Video has no valid duration")

    # Only a technical test. This is NOT a detected violation.
    test_time = round(info["duration_sec"] / 2, 3)

    def test_predictor(path):
        return [
            {
                "timecode_sec": test_time,
                "violation_id": "V04",
                "confidence": 0.99,
                "description": "TECHNICAL TEST ONLY - not a real violation"
            }
        ]

    result = analyze_video(
        video_path,
        predictor=test_predictor,
        output_dir=Path("runtime_evidence"),
    )

    violations = result["violations"]

    if len(violations) != 1:
        raise AssertionError("Expected one test event")

    frames = violations[0]["evidence_frames"]

    if not 1 <= len(frames) <= 3:
        raise AssertionError("Expected 1-3 evidence frames")

    for frame in frames:
        raw = base64.b64decode(
            frame["image_base64"],
            validate=True
        )

        if not raw.startswith(b"\xff\xd8\xff"):
            raise AssertionError("Invalid JPEG image")

    print("CV TEST PASSED")
    print("Test timestamp:", test_time)
    print("Evidence frames:", len(frames))
    print("JPEG Base64: OK")
    print("This does NOT confirm any real violation")


if __name__ == "__main__":
    main()
