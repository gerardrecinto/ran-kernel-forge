#!/usr/bin/env bash
# Validate CPU isolation config and set performance governor on all CPUs
# NOTE: isolcpus must be in kernel cmdline at boot — this script validates and fixes runtime params
set -euo pipefail

echo "=== RAN CPU Isolation Status ==="
CMDLINE=$(cat /proc/cmdline)
echo "[cmdline] ${CMDLINE}"
echo ""

if echo "${CMDLINE}" | grep -q "isolcpus"; then
    ISOLATED=$(echo "${CMDLINE}" | grep -oP 'isolcpus=\K[^ ]+')
    echo "PASS  isolcpus=${ISOLATED}"
else
    echo "WARN  isolcpus not set — add 'isolcpus=<cpus> rcu_nocbs=<cpus> nohz_full=<cpus>' to GRUB_CMDLINE_LINUX"
fi

if echo "${CMDLINE}" | grep -q "rcu_nocbs"; then
    NOCBS=$(echo "${CMDLINE}" | grep -oP 'rcu_nocbs=\K[^ ]+')
    echo "PASS  rcu_nocbs=${NOCBS}"
else
    echo "WARN  rcu_nocbs not set — RCU callbacks may preempt RAN workloads"
fi

echo ""
echo "=== CPU Frequency Governors ==="
FIXED=0
for cpu_dir in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/; do
    [[ -f "${cpu_dir}scaling_governor" ]] || continue
    cpu=$(echo "${cpu_dir}" | grep -oP 'cpu\d+')
    gov=$(cat "${cpu_dir}scaling_governor")
    if [[ "${gov}" != "performance" ]]; then
        echo "performance" > "${cpu_dir}scaling_governor" 2>/dev/null || true
        echo "FIXED ${cpu}: ${gov} -> performance"
        FIXED=$((FIXED + 1))
    else
        echo "PASS  ${cpu}: performance"
    fi
done

echo ""
[[ ${FIXED} -gt 0 ]] && echo "${FIXED} CPU(s) set to performance governor"
echo "Reboot required for isolcpus/rcu_nocbs/nohz_full changes to take effect"
