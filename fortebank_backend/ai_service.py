
from ml_pipeline import analyze_video


def analyze_video_ai(video_path: str) -> dict:
    """
    Main Backend -> ML/CV adapter.

    A trained predictor from participant 1
    must be connected before real inference works.
    """

    # No predictor is supplied yet.
    # ml_pipeline will raise a clear configuration error.
    return analyze_video(
        video_path=video_path,
        predictor=None,
        confidence_threshold=0.65,
        output_dir="runtime_evidence",
    )
