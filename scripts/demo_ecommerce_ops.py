"""Run a local demo for E-commerce Ops Agent Mini."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ecommerce_ops.agent import EcommerceOpsAgent


DEMO_QUERIES = {
    "product": "哪些商品库存不足或转化率低但曝光高？",
    "campaign": "本周活动效果怎么样？哪些活动ROI较低？",
    "task": "有哪些高优先级任务还没完成？",
    "report": "生成一份商家运营日报",
    "message": "生成一段给商家的提醒文案",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="E-commerce Ops Agent Mini — Demo CLI")
    parser.add_argument("--query", "-q", help="Natural language ops query")
    parser.add_argument("--preset", "-p", choices=list(DEMO_QUERIES), help="Use a preset demo query")
    parser.add_argument("--list-presets", action="store_true", help="List available preset queries")
    args = parser.parse_args()

    if args.list_presets:
        for key, query in DEMO_QUERIES.items():
            print(f"  {key}: {query}")
        return

    query = args.query or (DEMO_QUERIES.get(args.preset or "") if args.preset else None)
    if not query:
        print("Please provide --query or --preset. Use --list-presets to see available presets.")
        print("\nExample:")
        print('  python scripts/demo_ecommerce_ops.py --query "哪些商品库存不足？"')
        print("  python scripts/demo_ecommerce_ops.py --preset report")
        return

    agent = EcommerceOpsAgent()
    result = agent.run(query=query)

    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    print(f"\nSelected Tool: {result.selected_tool}")
    print(f"Used Tools: {', '.join(result.used_tools)}")
    print(f"Report Path: {result.report_path or 'N/A'}")
    print(f"\n--- Trace ---")
    for step in result.trace:
        print(f"  [{step.role}] {step.action} -> {step.status}")
        if step.detail:
            print(f"    {step.detail}")

    print(f"\n--- Answer ---")
    print(result.answer[:2000])

    if result.data_preview:
        print(f"\n--- Data Preview ({len(result.data_preview)} rows) ---")
        for row in result.data_preview[:3]:
            print(f"  {row}")


if __name__ == "__main__":
    main()
