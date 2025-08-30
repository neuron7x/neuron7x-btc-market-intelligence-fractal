#!/usr/bin/env python3
"""Run end-to-end evaluation on bundled real examples.

The script loads each ``real_*.json`` file in this directory. Each file
contains an ``input`` object compatible with the CLI along with a
``reference_overall_signal`` value. For every example we invoke the CLI,
collect the resulting ``overall_signal`` and compute basic quality
metrics against the reference: absolute error per example, overall MAE
and Pearson correlation across examples.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from statistics import mean
from tempfile import TemporaryDirectory
from typing import Tuple, List

ROOT = Path(__file__).resolve().parents[1]
CLI = "cli.btcmi"

def run_example(path: Path) -> Tuple[float, float]:
    """Run CLI for one example file and return predicted and reference signals."""
    data = json.loads(path.read_text(encoding="utf-8"))
    inp = data["input"]
    ref = float(data["reference_overall_signal"])

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        input_path = tmpdir / "input.json"
        output_path = tmpdir / "output.json"
        input_path.write_text(json.dumps(inp), encoding="utf-8")
        cmd = [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(input_path),
            "--out",
            str(output_path),
            "--mode",
            inp.get("mode", "v1"),
        ]
        subprocess.run(cmd, check=True)
        out = json.loads(output_path.read_text(encoding="utf-8"))
    pred = float(out["summary"]["overall_signal"])
    return pred, ref

def correlation(xs: List[float], ys: List[float]) -> float:
    """Compute Pearson correlation coefficient between two sequences."""
    if not xs or not ys:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = sum((x - mx) ** 2 for x in xs)
    den_y = sum((y - my) ** 2 for y in ys)
    denom = (den_x * den_y) ** 0.5
    return num / denom if denom else 0.0

def main() -> int:
    example_dir = Path(__file__).resolve().parent
    preds: List[float] = []
    refs: List[float] = []
    for path in sorted(example_dir.glob("real_*.json")):
        pred, ref = run_example(path)
        preds.append(pred)
        refs.append(ref)
        print(
            f"{path.name}: predicted={pred:.6f} reference={ref:.6f} "
            f"abs_error={abs(pred - ref):.6f}"
        )
    if not preds:
        print("No real_*.json examples found.")
        return 1
    mae = sum(abs(p - r) for p, r in zip(preds, refs)) / len(preds)
    corr = correlation(preds, refs)
    print(f"MAE: {mae:.6f}")
    print(f"Correlation: {corr:.6f}")
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
