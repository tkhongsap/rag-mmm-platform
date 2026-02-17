"""RAG evaluation runner — sends questions to the agent and generates a markdown report."""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = EVAL_DIR / "qa_dataset.json"
REPORTS_DIR = EVAL_DIR / "reports"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EvalItem:
    id: str
    category: str
    question: str
    ground_truth: str
    required_facts: list[str]
    match_mode: str  # "any", "all", or "all_groups"
    fact_groups: list[list[str]] = field(default_factory=list)


@dataclass
class EvalResult:
    item: EvalItem
    answer: str
    passed: bool
    matched_facts: list[str]
    missing_facts: list[str]
    elapsed_seconds: float
    error: str | None = None


# ---------------------------------------------------------------------------
# Dataset loader
# ---------------------------------------------------------------------------

def load_dataset(path: Path) -> list[EvalItem]:
    """Parse the JSON dataset file and return a list of EvalItem."""
    with open(path) as f:
        data = json.load(f)

    items: list[EvalItem] = []
    for raw in data["items"]:
        items.append(EvalItem(
            id=raw["id"],
            category=raw["category"],
            question=raw["question"],
            ground_truth=raw["ground_truth"],
            required_facts=raw["required_facts"],
            match_mode=raw.get("match_mode", "any"),
            fact_groups=raw.get("fact_groups", []),
        ))
    return items


# ---------------------------------------------------------------------------
# Answer checking
# ---------------------------------------------------------------------------

def check_answer(answer: str, item: EvalItem) -> tuple[bool, list[str], list[str]]:
    """Check whether the answer contains the required facts.

    Returns (passed, matched_facts, missing_facts).
    """
    answer_lower = answer.lower()
    matched: list[str] = []
    missing: list[str] = []

    if item.match_mode == "any":
        # Pass if ANY required fact appears
        for fact in item.required_facts:
            if fact.lower() in answer_lower:
                matched.append(fact)
        passed = len(matched) > 0
        if not passed:
            missing = list(item.required_facts)

    elif item.match_mode == "all":
        # Pass if ALL required facts appear
        for fact in item.required_facts:
            if fact.lower() in answer_lower:
                matched.append(fact)
            else:
                missing.append(fact)
        passed = len(missing) == 0

    elif item.match_mode == "all_groups":
        # Pass if at least one fact from EACH group matches
        for group in item.fact_groups:
            group_matched = False
            for fact in group:
                if fact.lower() in answer_lower:
                    matched.append(fact)
                    group_matched = True
                    break
            if not group_matched:
                missing.append(f"[group: {', '.join(group)}]")
        passed = len(missing) == 0

    else:
        # Fallback: treat as "any"
        for fact in item.required_facts:
            if fact.lower() in answer_lower:
                matched.append(fact)
        passed = len(matched) > 0
        if not passed:
            missing = list(item.required_facts)

    return passed, matched, missing


# ---------------------------------------------------------------------------
# Single question runner
# ---------------------------------------------------------------------------

async def run_single(item: EvalItem) -> EvalResult:
    """Send one question to the RAG agent and evaluate the response."""
    from src.platform.api.rag_agent import ask_marketing_question

    start = time.monotonic()
    try:
        answer = await ask_marketing_question(item.question)
    except Exception as exc:
        elapsed = time.monotonic() - start
        return EvalResult(
            item=item,
            answer="",
            passed=False,
            matched_facts=[],
            missing_facts=list(item.required_facts),
            elapsed_seconds=round(elapsed, 1),
            error=str(exc),
        )

    elapsed = time.monotonic() - start
    passed, matched, missing = check_answer(answer, item)

    return EvalResult(
        item=item,
        answer=answer,
        passed=passed,
        matched_facts=matched,
        missing_facts=missing,
        elapsed_seconds=round(elapsed, 1),
    )


# ---------------------------------------------------------------------------
# Run all questions (sequential)
# ---------------------------------------------------------------------------

async def run_all(items: list[EvalItem]) -> list[EvalResult]:
    """Run all eval items sequentially, printing progress."""
    results: list[EvalResult] = []
    total = len(items)

    for i, item in enumerate(items, 1):
        short_q = item.question[:50] + ("..." if len(item.question) > 50 else "")
        print(f"[{i}/{total}] {item.id}: {short_q}", end=" ", flush=True)

        result = await run_single(item)
        status = "PASS" if result.passed else ("ERROR" if result.error else "FAIL")
        print(f"-> {status} ({result.elapsed_seconds}s)")

        results.append(result)

    return results


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_report(results: list[EvalResult], output_path: Path) -> None:
    """Write a markdown evaluation report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    times = [r.elapsed_seconds for r in results]

    lines: list[str] = []
    lines.append("# RAG Evaluation Report\n")
    lines.append(f"**Generated:** {now}  |  **Dataset:** {total} questions\n")

    # --- Summary table ---
    lines.append("## Summary\n")
    lines.append("| # | Question | Category | Result | Time |")
    lines.append("|---|----------|----------|--------|------|")
    for r in results:
        status = "PASS" if r.passed else ("ERROR" if r.error else "FAIL")
        short_q = r.item.question[:55] + ("..." if len(r.item.question) > 55 else "")
        lines.append(f"| {r.item.id} | {short_q} | {r.item.category} | **{status}** | {r.elapsed_seconds}s |")

    lines.append("")
    lines.append(f"**Results:** {passed}/{total} passed ({passed/total*100:.1f}%)  |  **Total time:** {sum(times):.1f}s\n")

    # --- Detailed results ---
    lines.append("## Detailed Results\n")
    for r in results:
        status = "PASS" if r.passed else ("ERROR" if r.error else "FAIL")
        lines.append(f"### {r.item.id} — {status} ({r.elapsed_seconds}s)\n")
        lines.append(f"**Question:** {r.item.question}\n")
        lines.append(f"**Ground Truth:** {r.item.ground_truth}\n")

        if r.matched_facts:
            lines.append(f"**Matched Facts:** {', '.join(r.matched_facts)}")
        if r.missing_facts:
            lines.append(f"**Missing Facts:** {', '.join(r.missing_facts)}")
        if r.error:
            lines.append(f"**Error:** `{r.error}`")

        lines.append("")
        if r.answer:
            # Indent the full answer as a blockquote
            answer_lines = r.answer.strip().split("\n")
            lines.append("**Agent Answer:**\n")
            for al in answer_lines:
                lines.append(f"> {al}")
        else:
            lines.append("**Agent Answer:** *(no response)*")

        lines.append("\n---\n")

    # --- Timing distribution ---
    lines.append("## Timing Distribution\n")
    if times:
        lines.append(f"- **Min:** {min(times):.1f}s")
        lines.append(f"- **Max:** {max(times):.1f}s")
        lines.append(f"- **Mean:** {statistics.mean(times):.1f}s")
        lines.append(f"- **Median:** {statistics.median(times):.1f}s")
        lines.append(f"- **Total:** {sum(times):.1f}s")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to: {output_path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAG evaluation and generate a report")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to the Q&A dataset JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for the markdown report (default: auto-timestamped in reports/)",
    )
    args = parser.parse_args()

    if args.output is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = REPORTS_DIR / f"eval_{ts}.md"

    print(f"Loading dataset: {args.dataset}")
    items = load_dataset(args.dataset)
    print(f"Loaded {len(items)} questions\n")

    results = asyncio.run(run_all(items))

    generate_report(results, args.output)

    passed = sum(1 for r in results if r.passed)
    print(f"\nDone: {passed}/{len(results)} passed")


if __name__ == "__main__":
    main()
