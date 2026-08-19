# 5G RU kernel validation image
# Includes: linuxptp, ethtool, TSN tools, rt-tests, latency checker
FROM ubuntu:25.10@sha256:7cc5e35f6567ee8c66d2abb4aab0fd866669e6207c237c3a8f0947a5c7f17092

RUN apt-get update && apt-get install -y --no-install-recommends \
    linuxptp \
    ethtool \
    iproute2 \
    rt-tests \
    python3 \
    util-linux \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ran-ru

COPY scripts/ ./scripts/
COPY tests/ ./tests/
RUN chmod +x ./scripts/*.sh

LABEL org.opencontainers.image.title="5G RU Kernel Validation Toolkit" \
      org.opencontainers.image.description="PTP/IEEE 1588, TSN/ETF, and fronthaul timing validation for 5G Radio Unit workloads (O-RAN 7.2x)" \
      org.opencontainers.image.vendor="gerardrecinto" \
      org.opencontainers.image.source="https://github.com/gerardrecinto/ran-kernel-forge"

HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python3 /opt/ran-ru/tests/latency_check.py --quick || exit 1

ENTRYPOINT ["python3", "/opt/ran-ru/tests/latency_check.py"]
