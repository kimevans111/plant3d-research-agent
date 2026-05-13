"""Demo lightweight Skill Layer selection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.executor import SkillExecutor  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Demo Plant3D Skill Layer selection.")
    parser.add_argument("--query", required=True, help="User query to route to a skill.")
    parser.add_argument(
        "--file-path",
        action="append",
        default=[],
        help="Optional file path. Repeat this argument for multiple files.",
    )
    parser.add_argument("--task-type", default=None, help="Optional explicit task type.")
    return parser.parse_args()


def main() -> None:
    """Run the skill selector and print JSON output."""
    args = parse_args()
    output = SkillExecutor().execute(
        query=args.query,
        file_paths=args.file_path,
        task_type=args.task_type,
    )
    print(json.dumps(output.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
