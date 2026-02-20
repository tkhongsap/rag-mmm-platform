#!/usr/bin/env python3
"""
Orchestrator script for synthetic data generation.

Runs all generator modules in dependency order, validates outputs,
and prints summary statistics.

Usage:
    .venv/bin/python data/generators/generate_all.py
    .venv/bin/python data/generators/generate_all.py --validate-only
"""

import argparse
import os
import sys
import time
import importlib

# Ensure project root is on the path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)


def _print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def _print_step(step_num: int, total: int, description: str) -> None:
    """Print a progress step."""
    print(f"\n  [{step_num}/{total}] {description}...")


def _file_summary(directory: str) -> list:
    """List CSV and MD files with row counts and sizes."""
    summaries = []
    for root, _, files in os.walk(directory):
        for f in sorted(files):
            if f.endswith((".csv", ".md")):
                path = os.path.join(root, f)
                size_bytes = os.path.getsize(path)
                row_count = None
                if f.endswith(".csv"):
                    # Count lines (subtract 1 for header)
                    with open(path, "r") as fh:
                        row_count = sum(1 for _ in fh) - 1
                rel_path = os.path.relpath(path, PROJECT_ROOT)
                summaries.append({
                    "file": rel_path,
                    "rows": row_count,
                    "size_kb": round(size_bytes / 1024, 1),
                })
    return summaries


def _import_generator(module_name: str):
    """Dynamically import a generator module."""
    return importlib.import_module(f"data.generators.{module_name}")


def run_generation(*, use_ai: bool = False) -> bool:
    """
    Run all generators in dependency order.
    Returns True if all steps succeeded.
    """
    from data.generators.config import (
        RAW_DIR, CONTRACTS_DIR, MMM_DIR, CHANNEL_BUDGETS_GBP, UK_TOTAL_ANNUAL_BUDGET
    )

    total_steps = 8
    success = True
    start_time = time.time()

    _print_header("SYNTHETIC DATA GENERATION — ORCHESTRATOR")
    print(f"  Output directories:")
    print(f"    Raw data:   {RAW_DIR}")
    print(f"    Contracts:  {CONTRACTS_DIR}")
    print(f"    MMM data:   {MMM_DIR}")

    # Step 1: Config (already loaded on import)
    _print_step(1, total_steps, "Loading master configuration")
    from data.generators import config  # noqa: F811
    print(f"    Date range: {config.START_DATE} to {config.END_DATE}")
    print(f"    Markets: {', '.join(config.MARKETS.keys())}")
    print(f"    Channels: {len(config.ALL_CHANNELS)}")
    print(f"    Dealers: {config.NUM_DEALERS} ({config.NUM_LAUNCH_DEALERS} launch)")
    print(f"    OK")

    # Step 2: External data — economic indicators, competitor spend
    _print_step(2, total_steps, "Generating external context data")
    try:
        external_mod = _import_generator("external_data")
        external_mod.generate()
        print(f"    OK")
    except ImportError:
        print(f"    SKIPPED — module not yet implemented")
    except Exception as e:
        print(f"    ERROR: {e}")
        success = False

    # Step 3: Events calendar
    _print_step(3, total_steps, "Generating events calendar")
    try:
        events_mod = _import_generator("events")
        events_mod.generate()
        print(f"    OK")
    except ImportError:
        print(f"    SKIPPED — module not yet implemented")
    except Exception as e:
        print(f"    ERROR: {e}")
        success = False

    # Step 4: Digital media (6 CSVs)
    _print_step(4, total_steps, "Generating digital media datasets")
    try:
        digital_mod = _import_generator("digital_media")
        digital_mod.generate()
        print(f"    OK")
    except ImportError:
        print(f"    SKIPPED — module not yet implemented")
    except Exception as e:
        print(f"    ERROR: {e}")
        success = False

    # Step 5: Traditional media (4 CSVs)
    _print_step(5, total_steps, "Generating traditional media datasets")
    try:
        traditional_mod = _import_generator("traditional_media")
        traditional_mod.generate()
        print(f"    OK")
    except ImportError:
        print(f"    SKIPPED — module not yet implemented")
    except Exception as e:
        print(f"    ERROR: {e}")
        success = False

    # Step 6: Sales pipeline (4 CSVs)
    _print_step(6, total_steps, "Generating sales pipeline datasets")
    try:
        sales_mod = _import_generator("sales_pipeline")
        sales_mod.generate()
        print(f"    OK")
    except ImportError:
        print(f"    SKIPPED — module not yet implemented")
    except Exception as e:
        print(f"    ERROR: {e}")
        success = False

    # Step 7: Vendor contracts (7 markdown docs)
    _print_step(7, total_steps, "Generating vendor contract documents")
    try:
        contracts_mod = _import_generator("contracts")
        contracts_mod.generate()
        print(f"    OK")
    except ImportError:
        print(f"    SKIPPED — module not yet implemented")
    except Exception as e:
        print(f"    ERROR: {e}")
        success = False

    # Step 8: Campaign asset images (~50 PNGs + manifest)
    _print_step(8, total_steps, "Generating campaign asset images")
    try:
        assets_mod = _import_generator("assets")
        assets_mod.generate(use_ai=use_ai or None)
        print(f"    OK")
    except ImportError:
        print(f"    SKIPPED — module not yet implemented")
    except Exception as e:
        print(f"    ERROR: {e}")
        success = False

    elapsed = time.time() - start_time
    print(f"\n  Generation completed in {elapsed:.1f}s")
    return success


def run_aggregation() -> bool:
    """
    Aggregate raw CSVs into MMM-ready datasets.
    Returns True if aggregation succeeded.
    """
    _print_header("AGGREGATING MMM-READY DATA")
    try:
        agg_mod = _import_generator("aggregate_mmm")
        agg_mod.aggregate_mmm_data()
        print(f"    OK")
        return True
    except ImportError:
        print(f"    SKIPPED — module not yet implemented")
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def run_validation() -> bool:
    """
    Run all validators on generated data.
    Returns True if all validations pass.
    """
    _print_header("RUNNING VALIDATORS")
    try:
        validators_mod = _import_generator("validators")
        result = validators_mod.validate_all()
        if result:
            print(f"    ALL VALIDATIONS PASSED")
        else:
            print(f"    SOME VALIDATIONS FAILED — see details above")
        return result
    except ImportError:
        print(f"    SKIPPED — validators module not yet implemented")
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def print_summary() -> None:
    """Print summary statistics for all generated files."""
    from data.generators.config import RAW_DIR, CONTRACTS_DIR, MMM_DIR, DATA_DIR

    _print_header("GENERATION SUMMARY")

    # Gather files from all output directories
    all_summaries = []
    for directory in [RAW_DIR, CONTRACTS_DIR, MMM_DIR]:
        all_summaries.extend(_file_summary(directory))

    if not all_summaries:
        print("  No generated files found.")
        return

    # Print table
    print(f"\n  {'File':<55s} {'Rows':>8s} {'Size':>10s}")
    print(f"  {'-' * 55} {'-' * 8} {'-' * 10}")

    total_rows = 0
    total_size = 0.0
    csv_count = 0
    md_count = 0

    for s in all_summaries:
        row_str = f"{s['rows']:,}" if s['rows'] is not None else "—"
        size_str = f"{s['size_kb']:.1f} KB"
        print(f"  {s['file']:<55s} {row_str:>8s} {size_str:>10s}")

        if s['rows'] is not None:
            total_rows += s['rows']
            csv_count += 1
        else:
            md_count += 1
        total_size += s['size_kb']

    print(f"  {'-' * 55} {'-' * 8} {'-' * 10}")
    print(f"  {'TOTAL':<55s} {total_rows:>8,} {total_size:>9.1f} KB")
    print(f"\n  CSV files: {csv_count}, Markdown docs: {md_count}")

    # Spend verification
    try:
        import pandas as pd
        from data.generators.config import CHANNEL_BUDGETS_GBP

        print(f"\n  --- Spend Verification ---")
        total_expected = sum(CHANNEL_BUDGETS_GBP.values())
        total_actual = 0.0

        for root, _, files in os.walk(RAW_DIR):
            for f in files:
                if not f.endswith(".csv") or f == "competitor_spend.csv":
                    continue
                path = os.path.join(root, f)
                try:
                    df = pd.read_csv(path)
                    spend_cols = [c for c in df.columns if c.lower() == "spend"]
                    for col in spend_cols:
                        channel_spend = df[col].sum()
                        if channel_spend > 0:
                            total_actual += channel_spend
                except Exception:
                    pass

        if total_actual > 0:
            print(f"    Expected total UK spend: £{total_expected:>14,.2f}")
            print(f"    Actual total across CSVs: £{total_actual:>14,.2f}")
            deviation = abs(total_actual - total_expected) / total_expected * 100
            status = "OK" if deviation < 5 else "WARNING"
            print(f"    Deviation: {deviation:.1f}% [{status}]")
        else:
            print(f"    No spend data found in CSVs (generation may be pending)")

    except Exception as e:
        print(f"    Spend verification skipped: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Synthetic data generation orchestrator"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Skip generation and only run validators",
    )
    parser.add_argument(
        "--ai",
        action="store_true",
        help="Use OpenAI gpt-image-1.5 for campaign asset images",
    )
    args = parser.parse_args()

    overall_start = time.time()

    if args.validate_only:
        _print_header("VALIDATE-ONLY MODE")
        valid = run_validation()
        print_summary()
    else:
        gen_ok = run_generation(use_ai=args.ai)
        agg_ok = run_aggregation()
        valid = run_validation()
        print_summary()

    total_elapsed = time.time() - overall_start

    _print_header("DONE")
    print(f"  Total elapsed time: {total_elapsed:.1f}s")

    if not args.validate_only:
        print(f"\n  To re-validate only:")
        print(f"    .venv/bin/python data/generators/generate_all.py --validate-only")

    print()


if __name__ == "__main__":
    main()
