
import time
from pathlib import Path

from evidence_service import extract_evidence


def analyze_video_ai(video_path: str) -> dict:
    """
    Временный адаптер AI.
    Позже сюда подключается модель участника 1.
    """

    if not Path(video_path).exists():
        raise ValueError("Video file not found")

    time.sleep(2)

    # ТЕСТОВОЕ событие.
    # Позже это должен возвращать настоящий AI.
    detected_events = [
        {
            "type": "test_violation",
            "timecode_sec": 1.0,
            "description": "TEST ONLY: simulated violation",
            "confidence": 0.99,
            "legal_reference": None
        }
    ]

    violations = []

    for event in detected_events:
        frame = extract_evidence(
            video_path,
            event["timecode_sec"]
        )

        violations.append({
            "type": event["type"],
            "timecode_sec": event["timecode_sec"],
            "description": event["description"],
            "confidence": event["confidence"],
            "legal_reference": event["legal_reference"],
            "evidence_frames": [frame]
        })

    return {
        "verdict": (
            "violation" if violations
            else "no_violation"
        ),
        "violations": violations
    }
