"""Command-line interface for reproducible YieldGuard workflows."""

from __future__ import annotations

import argparse
import json

from yieldguard.acquire import acquire_dataset
from yieldguard.config import load_config
from yieldguard.pipeline import build_phase1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yieldguard")
    subcommands = parser.add_subparsers(dest="command", required=True)
    acquire = subcommands.add_parser("acquire", help="Download and validate UCI SECOM")
    acquire.add_argument("--force", action="store_true", help="Download the archive again")
    subcommands.add_parser(
        "build-phase1", help="Validate SECOM, audit trust, choose splits, and build DuckDB"
    )
    return parser


def main() -> None:
    """Run the requested pipeline command."""
    args = _parser().parse_args()
    config = load_config()
    if args.command == "acquire":
        result = acquire_dataset(config, force=args.force)
    else:
        result = build_phase1(config)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
