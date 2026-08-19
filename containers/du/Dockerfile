# 5G DU kernel validation image
# Includes: cyclictest, rt-tests, latency checker, tuning scripts
FROM ubuntu:25.10@sha256:7cc5e35f6567ee8c66d2abb4aab0fd866669e6207c237c3a8f0947a5c7f17092

RUN apt-get update && apt-get install -y --no-install-recommends \
    rt-tests \
    cpufrequtils \
    linux-tools-generic \
    numactl \
    util-linux \
    procps \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ran-du

COPY scripts/ ./scripts/
COPY tests/ ./tests/
RUN chmod +x ./scripts/*.sh

LABEL org.opencontainers.image.title="5G DU Kernel Validation Toolkit" \
      org.opencontainers.image.description="RT kernel tuning scripts and latency validation for 5G Distributed Unit workloads" \
      org.opencontainers.image.vendor="gerardrecinto" \
      org.opencontainers.image.source="https://github.com/gerardrecinto/ran-kernel-forge"

HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python3 /opt/ran-du/tests/latency_check.py --quick || exit 1

ENTRYPOINT ["python3", "/opt/ran-du/tests/latency_check.py"]
