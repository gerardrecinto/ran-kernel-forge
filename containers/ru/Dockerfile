# 5G RU kernel validation image
# Includes: linuxptp, ethtool, TSN tools, rt-tests, latency checker
FROM ubuntu:22.04@sha256:4f838adc7181d9039ac795a7d0aba05a9bd9ecd480d294483169c5def983b64d

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
