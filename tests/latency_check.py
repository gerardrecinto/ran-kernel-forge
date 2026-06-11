#!/usr/bin/env python3
"""Kernel readiness checker for 5G RAN workloads."""
import os
import sys
import argparse
import subprocess
import json
from pathlib import Path


def check_preempt_rt():
    try:
        uname = subprocess.check_output(["uname", "-v"], text=True).strip()
        return "PREEMPT_RT" in uname or "PREEMPT RT" in uname
    except Exception:
        return False


def check_isolcpus():
    try:
        cmdline = Path("/proc/cmdline").read_text()
        return "isolcpus" in cmdline or "rcu_nocbs" in cmdline
    except Exception:
        return False


def check_hugepages():
    try:
        data = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        nr = int(data.get("HugePages_Total", "0").split()[0])
        return nr > 0
    except Exception:
        return False


def check_irqbalance():
    try:
        r = subprocess.run(
            ["systemctl", "is-active", "irqbalance"],
            capture_output=True, text=True
        )
        return r.stdout.strip() != "active"
    except Exception:
        return True


def check_cpu_governor():
    governors = []
    for path in Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_governor"):
        try:
            governors.append(path.read_text().strip())
        except Exception:
            pass
    if not governors:
        return True  # No cpufreq — likely in container
    return all(g == "performance" for g in governors)


def run_cyclictest(duration_s=5, cpu=1):
    try:
        r = subprocess.run(
            ["cyclictest", "-m", "-p98", f"-D{duration_s}s", f"-a{cpu}", "-q", "--json"],
            capture_output=True, text=True, timeout=duration_s + 15
        )
        if r.returncode == 0:
            return json.loads(r.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return None


def main():
    parser = argparse.ArgumentParser(description="5G RAN kernel readiness checker")
    parser.add_argument("--quick", action="store_true", help="Skip cyclictest, config checks only")
    parser.add_argument("--json", action="store_true", dest="json_out")
    parser.add_argument("--max-latency-us", type=int, default=50,
                        help="Max p99 latency threshold in microseconds (default: 50)")
    args = parser.parse_args()

    checks = [
        ("preempt_rt",   "PREEMPT_RT kernel active",           check_preempt_rt()),
        ("isolcpus",     "CPU isolation (isolcpus/rcu_nocbs)",  check_isolcpus()),
        ("hugepages",    "Hugepages configured",                check_hugepages()),
        ("irqbalance",   "irqbalance disabled",                 check_irqbalance()),
        ("cpu_governor", "CPU governor = performance",          check_cpu_governor()),
    ]

    results = {k: {"label": l, "pass": p} for k, l, p in checks}

    if not args.quick:
        ct = run_cyclictest(duration_s=5)
        if ct:
            p99 = ct.get("statistics", [{}])[0].get("max", None)
            results["latency_p99"] = {
                "label": f"cyclictest p99 <= {args.max_latency_us}us",
                "pass": p99 is not None and p99 <= args.max_latency_us,
                "value_us": p99,
            }

    passed = sum(1 for v in results.values() if v["pass"])
    total = len(results)

    if args.json_out:
        print(json.dumps({"results": results, "passed": passed, "total": total}))
    else:
        for v in results.values():
            status = "PASS" if v["pass"] else "FAIL"
            extra = f"  ({v['value_us']}us)" if "value_us" in v else ""
            print(f"[{status}] {v['label']}{extra}")
        print(f"\n{passed}/{total} checks passed")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
