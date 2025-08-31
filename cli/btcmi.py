#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from btcmi.logging_cfg import configure_logging, new_run_id
from btcmi.runner import run_v1, run_v2, run_nf3p
from btcmi.schema_util import SCHEMA_REGISTRY, load_json, validate_json


def main() -> int:
    configure_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(prog="btcmi")
    parser.add_argument(
        "--json-errors",
        action="store_true",
        help="Emit errors as JSON to stdout",
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    parser_run = subparsers.add_parser(
        "run", help="Produce BTCMI report from input JSON"
    )
    parser_run.add_argument(
        "--input", required=True, help="Input JSON file or '-' for stdin"
    )
    parser_run.add_argument("--out")
    parser_run.add_argument("--fixed-ts", dest="fixed_ts")
    parser_run.add_argument(
        "--mode",
        required=True,
        choices=("v1", "v2.fractal", "v2.nf3p"),
        dest="mode",
    )

    parser_validate = subparsers.add_parser(
        "validate", help="Validate JSON against schema"
    )
    parser_validate.add_argument("--schema", required=True, type=Path)
    parser_validate.add_argument("--data", required=True, type=Path)

    args = parser.parse_args()
    run_id = new_run_id()

    def report(error: str, level: str = "exception", **details) -> None:
        msg = details.pop("message", None)
        if args.json_errors:
            payload = {"error": error, "details": details}
            if msg is not None:
                payload["message"] = msg
            print(json.dumps(payload))
        else:
            if msg is not None:
                details["error_message"] = msg
            getattr(logger, level)(error, extra=details)

    if args.cmd == "run":
        if args.input == "-":
            try:
                data = json.load(sys.stdin)
            except json.JSONDecodeError as e:
                report("invalid_json", run_id=run_id, message=str(e))
                return 2
        else:
            try:
                data = load_json(args.input)
            except FileNotFoundError as e:
                report(
                    "input_file_not_found", run_id=run_id, path=args.input, message=str(e)
                )
                return 2
            except json.JSONDecodeError as e:
                report("invalid_json", run_id=run_id, message=str(e))
                return 2
        try:
            validate_json(data, SCHEMA_REGISTRY["input"])
        except Exception as e:
            report("input_schema_validation_failed", run_id=run_id, message=str(e))
            return 2

        # If explicit mode present, enforce consistency with --mode argument
        mode = data.get("mode")
        if mode not in (None, "v1", "v2.fractal", "v2.nf3p"):
            report("unknown_mode", level="error", run_id=run_id, mode=mode)
            return 2
        if mode is not None and mode != args.mode:
            logger.warning("mode_mismatch", extra={"run_id": run_id, "mode": mode})

        try:
            if args.mode == "v2.fractal":
                out = run_v2(data, args.fixed_ts, args.out)
            elif args.mode == "v2.nf3p":
                out = run_nf3p(data, args.fixed_ts, args.out)
            else:
                out = run_v1(data, args.fixed_ts, args.out)
        except ValueError as e:
            report(
                "runner_error",
                run_id=run_id,
                mode=mode,
                message=str(e),
            )
            return 2
        if args.mode != "v2.nf3p":
            try:
                validate_json(out, SCHEMA_REGISTRY["output"])
            except Exception as e:
                report(
                    "output_schema_validation_failed",
                    run_id=run_id,
                    mode=mode,
                    message=str(e),
                )
                return 2
        if args.out is None:
            print(json.dumps(out, indent=2))
        logger.info(
            "run_ok",
            extra={
                "run_id": run_id,
                "mode": args.mode,
            },
        )
        return 0

    try:
        data = load_json(args.data)
    except FileNotFoundError as e:
        report(
            "data_file_not_found", run_id=run_id, path=str(args.data), message=str(e)
        )
        return 2
    except json.JSONDecodeError as e:
        report("invalid_json", run_id=run_id, message=str(e))
        return 2
    try:
        validate_json(data, args.schema)
    except FileNotFoundError as e:
        report(
            "schema_file_not_found", run_id=run_id, path=str(args.schema), message=str(e)
        )
        return 2
    except Exception as e:
        report("schema_validation_failed", run_id=run_id, message=str(e))
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
