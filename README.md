# ran-kernel-forge

[![CI](https://github.com/gerardrecinto/ran-kernel-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/gerardrecinto/ran-kernel-forge/actions/workflows/ci.yml)
[![Release](https://github.com/gerardrecinto/ran-kernel-forge/actions/workflows/release.yml/badge.svg)](https://github.com/gerardrecinto/ran-kernel-forge/actions/workflows/release.yml)

Linux kernel profiles and validation containers for 5G/6G RAN workloads. Covers Distributed Unit (DU), Central Unit (CU), and Radio Unit (RU) deployment on COTS x86\_64 hardware. Targets sub-1ms scheduling jitter for L1/L2 real-time processing and fronthaul synchronization.

## What it does

- **Kernel config fragments** — per-node-type `.config` fragments for PREEMPT_RT, CPU isolation, hugepages, DPDK/VFIO, and PTP (O-RAN fronthaul timing)
- **Tuning scripts** — hugepage allocation, IRQ affinity pinning, and CPU isolation validation; idempotent, re-runnable
- **Validation container** — Docker image with cyclictest, latency checker, and kernel config audit; runs in CI and on target nodes before workload deployment
- **CI gate** — every commit validates profile syntax, lints scripts, and builds both DU and CU containers

## Node profiles

| Profile | RT level | Primary workload | Key config |
|---------|----------|-----------------|------------|
| `du` | PREEMPT_RT | L1/L2 baseband, PDCP | isolcpus, rcu_nocbs, hugepages, VFIO |
| `cu` | PREEMPT_VOLUNTARY | RRC, PDCP, SDAP | SR-IOV, FQ_CODEL, high-throughput NIC |
| `ru` | PREEMPT_RT | eCPRI/O-RAN 7.2x fronthaul | PTP_1588, TSN/ETF, TAPRIO, isolcpus |

## Quick start

```bash
# Run kernel readiness check on a target node
docker run --privileged --pid=host \
  ghcr.io/gerardrecinto/ran-kernel-forge-du:latest

# Or clone and run locally
git clone https://github.com/gerardrecinto/ran-kernel-forge
cd ran-kernel-forge
python3 tests/latency_check.py --quick
```

## Tuning

```bash
# 1. Configure hugepages (2GB = 1024 x 2MB)
sudo ./scripts/tune-hugepages.sh 1024 2048

# 2. Pin IRQs to housekeeping CPUs 0-1, isolating CPUs 2-N for RAN
sudo ./scripts/tune-irq-affinity.sh "0,1" eth0

# 3. Validate CPU isolation and governor (informational — isolcpus set at boot)
sudo ./scripts/tune-cpu-isolation.sh
```

For persistent CPU isolation, add to `GRUB_CMDLINE_LINUX`:

```
isolcpus=2-N rcu_nocbs=2-N nohz_full=2-N intel_pstate=disable
```

## Applying a kernel config fragment

```bash
# On the target node, apply DU profile fragment to existing .config
scripts/apply-profile.sh profiles/du-profile.config /path/to/kernel-src
```

## Pull containers

```bash
# DU validation image
docker pull ghcr.io/gerardrecinto/ran-kernel-forge-du:latest

# CU validation image
docker pull ghcr.io/gerardrecinto/ran-kernel-forge-cu:latest
```

## Repo structure

```
ran-kernel-forge/
├── profiles/           # Kernel config fragments per node type
│   ├── du-profile.config
│   ├── cu-profile.config
│   └── ru-profile.config
├── containers/
│   ├── du/Dockerfile   # DU validation image (cyclictest, rt-tests)
│   └── cu/Dockerfile   # CU validation image
├── scripts/
│   ├── tune-hugepages.sh
│   ├── tune-irq-affinity.sh
│   ├── tune-cpu-isolation.sh
│   └── apply-profile.sh
├── tests/
│   └── latency_check.py  # Kernel readiness checker
└── .github/workflows/
    ├── ci.yml
    └── release.yml
```

## Target use cases

- Pre-flight validation before deploying 5G DU workloads on bare metal or edge nodes
- O-RAN CU/DU split deployment on Qualcomm, Intel, or COTS x86 platforms
- CI gate in RAN node provisioning pipelines (Ansible, Terraform, Helm)
- MWC / lab demo: reproduce standard DU tuning in under 5 minutes from cold node
