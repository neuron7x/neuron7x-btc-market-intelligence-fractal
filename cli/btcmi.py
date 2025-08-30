#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure local package importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from btcmi.logging_cfg import configure_logging, new_run_id
from btcmi.runner import run_v1, run_v2
from btcmi.schema_util import load_json, validate_json


def main() -> int:
    configure_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(prog="btcmi")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    parser_run = subparsers.add_parser(
        "run", help="Produce BTCMI report from input JSON"
    )
    parser_run.add_argument("--input", required=True)
    parser_run.add_argument("--out", required=True)
    parser_run.add_argument("--fixed-ts", dest="fixed_ts")
    parser_run.add_argument("--fractal", action="store_true")

    parser_validate = subparsers.add_parser(
        "validate", help="Validate JSON against schema"
    )
    parser_validate.add_argument("--schema", required=True, type=Path)
    parser_validate.add_argument("--data", required=True, type=Path)

    args = parser.parse_args()
    run_id = new_run_id()

    if args.cmd == "run":
        data = load_json(args.input)
        try:
            validate_json(
                data, Path(__file__).resolve().parents[1] / "input_schema.json"
            )
        except Exception:
            logger.warning("input_schema_validation_failed", extra={"run_id": run_id})

        # If explicit mode present, enforce consistency with --fractal flag
        mode = data.get("mode")
        if mode == "v1" and args.fractal:
            logger.warning("mode_flag_mismatch", extra={"run_id": run_id, "mode": mode})
        if mode == "v2.fractal" and not args.fractal:
            logger.warning("mode_flag_mismatch", extra={"run_id": run_id, "mode": mode})

        out = (
            run_v2(data, args.fixed_ts, args.out)
            if args.fractal or mode == "v2.fractal"
            else run_v1(data, args.fixed_ts, args.out)
        )
        try:
            validate_json(
                out, Path(__file__).resolve().parents[1] / "output_schema.json"
            )
        except Exception:
            logger.error(
                "output_schema_validation_failed",
                extra={"run_id": run_id, "mode": mode},
            )
            return 2
        logger.info(
            "run_ok",
            extra={
                "run_id": run_id,
                "mode": (
                    "v2.fractal" if (args.fractal or mode == "v2.fractal") else "v1"
                ),
            },
        )
        return 0

    data = load_json(args.data)
    try:
        validate_json(data, args.schema)
    except Exception:
        logger.exception("schema_validation_failed", extra={"run_id": run_id})
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
