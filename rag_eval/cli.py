"""Command-line entry point for RAG-Eval Mini."""

from __future__ import annotations

import argparse
from pathlib import Path

from rag_eval.evaluator import RagEvaluator


def parse_bool(value: str | bool) -> bool:
    """Parse a CLI boolean value."""
    if isinstance(value, bool):
        return value
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected true/false, got {value!r}")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run lightweight RAG retrieval evaluation.")
    parser.add_argument("--eval-file", default="examples/eval/rag_eval_questions.jsonl")
    parser.add_argument("--docs-dir", default="examples")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--output-dir", default="reports/rag_eval")
    parser.add_argument("--use-agent-answer", type=parse_bool, default=False)
    parser.add_argument("--retriever", choices=["keyword", "json", "chroma", "auto"], default="auto")
    parser.add_argument("--rebuild-index", type=parse_bool, default=False)
    return parser


def main() -> None:
    """Run RAG evaluation from the command line."""
    args = build_parser().parse_args()
    evaluator = RagEvaluator(
        eval_file=Path(args.eval_file),
        docs_dir=Path(args.docs_dir),
        top_k=args.top_k,
        output_dir=Path(args.output_dir),
        use_agent_answer=args.use_agent_answer,
        retriever=args.retriever,
        rebuild_index=args.rebuild_index,
    )
    result = evaluator.run()
    print(f"Summary JSON: {result['summary_path']}")
    print(f"Detail JSON: {result['detail_path']}")
    print(f"Markdown report: {result['report_path']}")


if __name__ == "__main__":
    main()
