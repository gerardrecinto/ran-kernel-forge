#!/usr/bin/env bash
# Merge a kernel config fragment into an existing .config
# Usage: ./apply-profile.sh <fragment.config> <kernel-src-dir>
set -euo pipefail

FRAGMENT="${1:-}"
KERNEL_SRC="${2:-}"

if [[ -z "${FRAGMENT}" || -z "${KERNEL_SRC}" ]]; then
    echo "Usage: $0 <fragment.config> <kernel-src-dir>"
    exit 1
fi

[[ -f "${FRAGMENT}" ]] || { echo "ERROR: fragment not found: ${FRAGMENT}"; exit 1; }
[[ -f "${KERNEL_SRC}/.config" ]] || { echo "ERROR: .config not found in ${KERNEL_SRC}"; exit 1; }
[[ -f "${KERNEL_SRC}/scripts/kconfig/merge_config.sh" ]] || { echo "ERROR: merge_config.sh not found — is this a kernel source tree?"; exit 1; }

echo "Applying $(basename ${FRAGMENT}) to ${KERNEL_SRC}/.config..."
cd "${KERNEL_SRC}"
./scripts/kconfig/merge_config.sh .config "${OLDPWD}/${FRAGMENT}"
echo "Profile applied. Run 'make olddefconfig' to resolve any remaining symbols."
