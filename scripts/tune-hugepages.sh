#!/usr/bin/env bash
# Configure hugepages for DPDK/PMD workloads on 5G DU/RU nodes
# Usage: ./tune-hugepages.sh [NR_PAGES] [SIZE_KB]
# Defaults: 1024 pages x 2MB = 2GB total
set -euo pipefail

NR_HUGEPAGES="${1:-1024}"
HUGEPAGE_SIZE_KB="${2:-2048}"

echo "Configuring ${NR_HUGEPAGES}x ${HUGEPAGE_SIZE_KB}kB hugepages..."

HUGEPAGE_DIR="/sys/kernel/mm/hugepages/hugepages-${HUGEPAGE_SIZE_KB}kB"
if [[ ! -d "${HUGEPAGE_DIR}" ]]; then
    echo "ERROR: hugepage size ${HUGEPAGE_SIZE_KB}kB not supported by this kernel"
    exit 1
fi

echo "${NR_HUGEPAGES}" > "${HUGEPAGE_DIR}/nr_hugepages"

if ! mountpoint -q /dev/hugepages; then
    mkdir -p /dev/hugepages
    mount -t hugetlbfs nodev /dev/hugepages -o "pagesize=${HUGEPAGE_SIZE_KB}k"
fi

ACTUAL=$(cat "${HUGEPAGE_DIR}/nr_hugepages")
echo "Allocated: ${ACTUAL}/${NR_HUGEPAGES} hugepages (${HUGEPAGE_SIZE_KB}kB each)"

if [[ "${ACTUAL}" -lt "${NR_HUGEPAGES}" ]]; then
    echo "ERROR: only ${ACTUAL} pages allocated — check available contiguous memory"
    exit 1
fi

echo "Hugepage configuration complete: $((ACTUAL * HUGEPAGE_SIZE_KB / 1024))MB reserved"
