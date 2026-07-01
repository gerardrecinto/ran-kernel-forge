# 5G CU kernel validation image
# Includes: network tuning tools, eBPF, latency checker
FROM ubuntu:26.04@sha256:53958ec7b67c2c9355df922dd08dbf0360611f8c3cdb656875e81873db9ffdba

RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 \
    ethtool \
    numactl \
    linux-tools-generic \
    util-linux \
    procps \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ran-cu

COPY scripts/ ./scripts/
COPY tests/ ./tests/
RUN chmod +x ./scripts/*.sh

LABEL org.opencontainers.image.title="5G CU Kernel Validation Toolkit" \
      org.opencontainers.image.description="Network tuning and validation for 5G Central Unit workloads" \
      org.opencontainers.image.vendor="gerardrecinto" \
      org.opencontainers.image.source="https://github.com/gerardrecinto/ran-kernel-forge"

HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python3 /opt/ran-cu/tests/latency_check.py --quick || exit 1

ENTRYPOINT ["python3", "/opt/ran-cu/tests/latency_check.py"]
