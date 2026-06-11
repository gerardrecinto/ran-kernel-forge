#!/usr/bin/env bash
# Pin IRQs to housekeeping CPUs, freeing RAN CPUs from interrupt noise
# Usage: ./tune-irq-affinity.sh <housekeeping_cpus> [nic_prefix]
# Example: ./tune-irq-affinity.sh "0,1" eth0
set -euo pipefail

HOUSEKEEPING_CPUS="${1:-0}"
NIC_PREFIX="${2:-}"

AFFINITY_MASK=$(python3 -c "
cpus = [int(c) for c in '${HOUSEKEEPING_CPUS}'.split(',')
mask = sum(1 << c for c in cpus)
print(hex(mask))
")

echo "Pinning all IRQs to CPUs ${HOUSEKEEPING_CPUS} (mask ${AFFINITY_MASK})..."

for irq_dir in /proc/irq/*/; do
    irq_num=$(basename "${irq_dir}")
    [[ "${irq_num}" == "*" ]] && continue
    echo "${AFFINITY_MASK}" > "${irq_dir}smp_affinity" 2>/dev/null || true
done

echo "All IRQs pinned to housekeeping CPUs"

if [[ -n "${NIC_PREFIX}" ]]; then
    echo "Setting ${NIC_PREFIX} NIC IRQ affinity..."
    while IFS= read -r irq; do
        [[ -z "${irq}" ]] && continue
        echo "${AFFINITY_MASK}" > "/proc/irq/${irq}/smp_affinity" 2>/dev/null && \
            echo "  IRQ ${irq} -> ${AFFINITY_MASK}" || true
    done < <(grep -i "${NIC_PREFIX}" /proc/interrupts | awk '{print $1}' | tr -d ':')
fi

echo "IRQ affinity configuration complete"
