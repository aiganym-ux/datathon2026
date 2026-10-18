"""ForteBank Datathon: ML -> CV evidence adapter.

IMPORTANT: object/pose detections are not violations. The predictor must be a trained
video/event classifier that returns semantic violation candidates. This module does not
invent events when no predictor is configured.
"""
from __future__ import annotations
import base64, json, re, unicodedata
from pathlib import Path
from typing import Callable, Any

HERE = Path(__file__).resolve().parent
CV_DIR = HERE / "ForteBank_CV"

# Candidate schema expected from participant 1's trained model:
# {"timecode_sec": 12.3, "violation_id": "V06", "confidence": 0.87,
#  "description": "..."}
Predictor = Callable[[str], list[dict[str, Any]]]


def _load_categories(path: Path = CV_DIR / "rules" / "categories.json") -> dict[str, dict]:
    if not path.exists():
        raise FileNotFoundError(f"Categories file not found: {path}")
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {str(row["id"]): row for row in rows if row.get("id")}


def _get_evidence(video_path: Path, time_sec: float, output_dir: Path) -> list[dict]:
    # Use participant 2's CV evidence extractor; add import path without requiring package install.
    import sys
    if str(CV_DIR) not in sys.path:
        sys.path.insert(0, str(CV_DIR))
    from evidence_generator import evidence_for_event
    return evidence_for_event(video_path, time_sec, offsets=(-0.3, 0.0, 0.3), output_dir=str(output_dir))


def analyze_video(video_path: str | Path, predictor: Predictor | None = None,
                  output_dir: str | Path | None = None, confidence_threshold: float = 0.65,
                  max_events: int = 100) -> dict:
    """Analyze with a semantic predictor, then attach CV-generated evidence.

    No predictor -> explicit configuration error, never fake 'no_violation' or pose-based events.
    """
    video = Path(video_path).resolve()
    if not video.is_file():
        raise FileNotFoundError(f"Video not found: {video}")
    if predictor is None:
        raise RuntimeError(
            "No trained violation predictor configured. Connect participant 1's model via "
            "predictor(video_path) -> list[dict]. The ForteBank_CV folder extracts evidence; "
            "it does not classify violations by itself."
        )
    out_dir = Path(output_dir) if output_dir else HERE / "runtime_evidence"
    out_dir.mkdir(parents=True, exist_ok=True)
    categories = _load_categories()
    candidates = predictor(str(video))
    if not isinstance(candidates, list):
        raise TypeError("predictor must return a list of candidate event dictionaries")

    events = []
    for item in candidates[:max_events]:
        if not isinstance(item, dict):
            continue
        try:
            timestamp = float(item["timecode_sec"])
            confidence = float(item.get("confidence", 0.0))
        except (KeyError, TypeError, ValueError):
            continue
        vid = str(item.get("violation_id", "")).strip().upper()
        # Only known semantic categories and confident classifier outputs can become events.
        if vid not in categories or not (0 <= timestamp) or confidence < confidence_threshold:
            continue
        category = categories[vid]
        evidence = _get_evidence(video, timestamp, out_dir)
        if not evidence:
            continue
        events.append({
            "timecode_sec": round(timestamp, 3),
            "timecode_mmss": f"{int(timestamp // 60):02d}:{int(timestamp % 60):02d}",
            "verdict": "violation",
            "violation_id": vid,
            "violation_type": category.get("name", vid),
            "description": str(item.get("description") or "Предполагаемое событие требует проверки по кадрам-доказательствам."),
            "confidence": round(confidence, 4),
            "regulation": {
                "status": category.get("regulation_status", "not_verified"),
                "document": category.get("document"),
                "clause": category.get("clause"),
                "source_url": category.get("source_url"),
            },
            "evidence_frames": evidence,
        })
    events.sort(key=lambda e: e["timecode_sec"])
    return {
        "video_id": video.stem,
        "status": "done",
        "verdict": "violation" if events else "no_violation",
        "violations": events,
        "meta": {
            "model_source": "participant_1_predictor",
            "evidence_source": "ForteBank_CV.evidence_generator",
            "confidence_threshold": confidence_threshold,
            "regulations_verified": all(e["regulation"]["status"] == "verified" for e in events),
            "warning": "no_violation означает отсутствие событий выше порога модели, а не доказательство абсолютного отсутствия нарушения",
        },
    }


def predictor_contract_example(video_path: str) -> list[dict]:
    """Replace this stub with the trained model. Deliberately returns no events."""
    raise NotImplementedError("Connect your trained classifier; do not infer violations from object presence alone.")
