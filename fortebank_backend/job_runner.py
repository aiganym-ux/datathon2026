
import json
import sys
from pathlib import Path

from ai_service import analyze_video_ai


def main():
    if len(sys.argv) != 3:
        raise ValueError("Expected video and result paths")

    video_path = sys.argv[1]
    result_path = Path(sys.argv[2])

    result = analyze_video_ai(video_path)

    with result_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
