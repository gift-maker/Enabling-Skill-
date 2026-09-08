#!/usr/bin/env python3
"""执行一条建模命令并记录命令、输入/输出哈希和日志。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


VALID_STATUS = {"exploratory", "baseline", "candidate", "final", "validation"}
RUN_HEADER = [
    "run_id", "timestamp", "question", "purpose", "status", "command",
    "inputs", "code", "parameters", "seed", "outputs", "return_code",
    "stdout", "stderr", "validation_status",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot(root: Path, values: list[str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for value in values:
        path = (root / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
        record: dict[str, object] = {"path": str(path), "exists": path.exists()}
        if path.is_file():
            record.update(size=path.stat().st_size, sha256=sha256(path))
        records.append(record)
    return records


def next_run_id(run_dir: Path) -> str:
    numbers = []
    for child in run_dir.glob("R*"):
        if child.name[1:].isdigit():
            numbers.append(int(child.name[1:]))
    return f"R{max(numbers, default=0) + 1:03d}"


def append_ledger(ledger: Path, row: dict[str, object]) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    if not ledger.exists():
        with ledger.open("w", encoding="utf-8-sig", newline="") as stream:
            csv.writer(stream).writerow(RUN_HEADER)
    with ledger.open("r", encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream))
    with ledger.open("a", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, extrasaction="ignore")
        writer.writerow({key: row.get(key, "") for key in header})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--status", choices=sorted(VALID_STATUS), required=True)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--code", action="append", default=[])
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--parameters", default="{}", help="JSON 对象")
    parser.add_argument("--seed", default="")
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    root = args.root.resolve()
    if (root / "结果").is_dir():
        ledger = root / "内部记录" / "运行记录.csv"
        runs = root / "结果" / "运行记录"
    elif (root / "4_结果").is_dir():
        ledger = root / "registries" / "run_ledger.csv"
        runs = root / "4_结果" / "runs"
    else:
        ledger = root / "内部记录" / "运行记录.csv"
        runs = root / "结果" / "运行记录"
    runs.mkdir(parents=True, exist_ok=True)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("缺少要执行的命令；在参数后使用 -- 命令")
    try:
        parameters = json.loads(args.parameters)
        if not isinstance(parameters, dict):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        parser.error("--parameters 必须是 JSON 对象")

    run_id = next_run_id(runs)
    run_path = runs / run_id
    run_path.mkdir()
    started = datetime.now(timezone.utc).isoformat()
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=args.timeout,
            check=False,
        )
        return_code = completed.returncode
        stdout, stderr = completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        return_code = 124
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + "\nTIMEOUT"

    (run_path / "stdout.txt").write_text(stdout, encoding="utf-8")
    (run_path / "stderr.txt").write_text(stderr, encoding="utf-8")
    record = {
        "run_id": run_id,
        "timestamp": started,
        "question": args.question,
        "purpose": args.purpose,
        "status": args.status,
        "command": command,
        "inputs": snapshot(root, args.input),
        "code": snapshot(root, args.code),
        "parameters": parameters,
        "seed": args.seed,
        "outputs": snapshot(root, args.output),
        "return_code": return_code,
        "stdout": str(run_path / "stdout.txt"),
        "stderr": str(run_path / "stderr.txt"),
        "validation_status": "pending",
    }
    (run_path / "record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    append_ledger(ledger, {**record, **{key: json.dumps(record[key], ensure_ascii=False) for key in ("command", "inputs", "code", "parameters", "outputs")}})
    print(run_id)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())

