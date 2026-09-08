"""生成复现清单 results/复现清单.json。

用法:
    python repro_manifest.py --project-root <PROJECT_ROOT> [--seed 42]
        [--command "python code/problem1.py"]
        [--inputs data/a.xlsx data/b.csv]
        [--param alpha=0.1] [--param max_iter=1000] [--package scipy]
        [--artifacts code/problem1.py results/problem1.csv]

记录随机种子、参数、输入与产物 SHA-256、运行环境与依赖版本，保证可复现。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dep_versions(extra_packages: list[str] | None = None) -> dict[str, str]:
    pkgs = [
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "openpyxl",
        "Pillow",
    ]
    pkgs.extend(extra_packages or [])
    pkgs = list(dict.fromkeys(pkgs))
    versions: dict[str, str] = {}
    for pkg in pkgs:
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "not-installed"
    return versions


def git_head(project_root: str) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", project_root, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:  # noqa: BLE001
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="生成复现清单")
    ap.add_argument("--project-root", required=True, help="项目根目录")
    ap.add_argument("--seed", default=None, help="随机种子")
    ap.add_argument("--command", default="", help="唯一复现命令")
    ap.add_argument("--inputs", nargs="*", default=[], help="输入数据文件（相对项目根）")
    ap.add_argument("--input", action="append", default=[], help="单个输入文件；可重复传入")
    ap.add_argument("--artifacts", nargs="*", default=[], help="代码、结果或图表文件（相对项目根）")
    ap.add_argument("--parameters", default="{}", help="模型参数 JSON；无法解析时按原始文本保存")
    ap.add_argument("--param", action="append", default=[], help="模型参数 key=value；可重复传入")
    ap.add_argument("--package", action="append", default=[], help="额外记录的依赖包；可重复传入")
    ap.add_argument("--runtime", default="python", help="运行环境，如 python 或 matlab")
    ap.add_argument("--runtime-version", default="", help="额外运行环境版本")
    ap.add_argument("--run-seconds", type=float, default=None, help="核心计算实测耗时（秒）")
    args = ap.parse_args()

    root = os.path.abspath(args.project_root)
    if not os.path.isdir(root):
        print(f"FAIL: 项目目录不存在: {root}")
        return 1

    inputs = list(dict.fromkeys([*args.inputs, *args.input]))
    input_hashes: dict[str, str] = {}
    for rel in inputs:
        path = os.path.join(root, rel)
        if os.path.isfile(path):
            input_hashes[rel] = sha256(path)
        else:
            input_hashes[rel] = "MISSING"

    artifact_hashes: dict[str, str] = {}
    for rel in args.artifacts:
        path = os.path.join(root, rel)
        artifact_hashes[rel] = sha256(path) if os.path.isfile(path) else "MISSING"

    try:
        parameters: object = json.loads(args.parameters)
    except json.JSONDecodeError:
        parameters = args.parameters
    if args.param:
        if not isinstance(parameters, dict):
            parameters = {"_raw": parameters}
        for item in args.param:
            if "=" not in item:
                print(f"FAIL: --param 必须为 key=value: {item}")
                return 1
            key, value = item.split("=", 1)
            if not key:
                print(f"FAIL: --param 键不能为空: {item}")
                return 1
            try:
                parameters[key] = json.loads(value)
            except json.JSONDecodeError:
                parameters[key] = value

    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "runtime": args.runtime,
        "runtime_version": args.runtime_version,
        "run_seconds": args.run_seconds,
        "seed": args.seed,
        "parameters": parameters,
        "command": args.command,
        "git_head": git_head(root),
        "input_files_sha256": input_hashes,
        "artifact_files_sha256": artifact_hashes,
        "dependencies": dep_versions(args.package),
    }

    results_dir = os.path.join(root, "results")
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, "复现清单.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print(f"复现清单已写入: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
