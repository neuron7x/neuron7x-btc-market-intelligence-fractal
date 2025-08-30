#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

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
    parser_run.add_argument("--input", required=True, help="Input JSON file or '-' for stdin")
    parser_run.add_argument("--out")
    parser_run.add_argument("--fixed-ts", dest="fixed_ts")
    parser_run.add_argument(
        "--mode", required=True, choices=("v1", "v2.fractal"), dest="mode"
    )

    parser_validate = subparsers.add_parser(
        "validate", help="Validate JSON against schema"
    )
    parser_validate.add_argument("--schema", required=True, type=Path)
    parser_validate.add_argument("--data", required=True, type=Path)

    args = parser.parse_args()
    run_id = new_run_id()

    if args.cmd == "run":
        if args.input == "-":
            data = json.load(sys.stdin)
        else:
            data = load_json(args.input)
        scenario = data.get("scenario")
        mode = data.get("mode")
        try:
            validate_json(
                data, Path(__file__).resolve().parents[1] / "input_schema.json"
            )
        except Exception:
            logger.exception(
                "input_schema_validation_failed",
                extra={"run_id": run_id, "mode": mode, "scenario": scenario},
            )
            return 2

        # If explicit mode present, enforce consistency with --mode argument
        if mode not in (None, "v1", "v2.fractal"):
            logger.error(
                "unknown_mode",
                extra={"run_id": run_id, "mode": mode, "scenario": scenario},
            )
            return 2
        if mode is not None and mode != args.mode:
            logger.warning(
                "mode_mismatch",
                extra={"run_id": run_id, "mode": mode, "scenario": scenario},
            )

        try:
            out = (
                run_v2(data, args.fixed_ts, args.out)
                if args.mode == "v2.fractal"
                else run_v1(data, args.fixed_ts, args.out)
            )
        except ValueError:
            logger.exception(
                "runner_error",
                extra={"run_id": run_id, "mode": mode, "scenario": scenario},
            )
            return 2
        try:
            validate_json(
                out, Path(__file__).resolve().parents[1] / "output_schema.json"
            )
        except Exception:
            logger.exception(
                "output_schema_validation_failed",
                extra={"run_id": run_id, "mode": mode, "scenario": scenario},
            )
            return 2
        if args.out is None:
            print(json.dumps(out, indent=2))
        logger.info(
            "run_ok",
            extra={
                "run_id": run_id,
                "mode": args.mode,
                "scenario": scenario,
            },
        )
        return 0

    data = load_json(args.data)
    scenario = data.get("scenario")
    mode = data.get("mode")
    try:
        validate_json(data, args.schema)
    except Exception:
        logger.exception(
            "schema_validation_failed",
            extra={"run_id": run_id, "mode": mode, "scenario": scenario},
        )
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
