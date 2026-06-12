#!/usr/bin/env python3
"""Unit tests for latency_check.py kernel readiness checks."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))
import latency_check as lc


class TestPreemptRt:
    def test_rt_kernel(self):
        with patch("subprocess.check_output", return_value="#1 SMP PREEMPT_RT"):
            assert lc.check_preempt_rt() is True

    def test_rt_kernel_with_space(self):
        with patch("subprocess.check_output", return_value="#1 PREEMPT RT Debian"):
            assert lc.check_preempt_rt() is True

    def test_non_rt_kernel(self):
        with patch("subprocess.check_output", return_value="#1 SMP Debian 5.15"):
            assert lc.check_preempt_rt() is False

    def test_subprocess_failure(self):
        with patch("subprocess.check_output", side_effect=FileNotFoundError):
            assert lc.check_preempt_rt() is False


class TestIsolcpus:
    def _with_cmdline(self, content):
        with patch("latency_check.Path") as M:
            M.return_value.read_text.return_value = content
            return lc.check_isolcpus()

    def test_isolcpus_flag(self):
        assert self._with_cmdline("isolcpus=2,3 nohz_full=2,3") is True

    def test_rcu_nocbs_flag(self):
        assert self._with_cmdline("rcu_nocbs=2,3") is True

    def test_both_absent(self):
        assert self._with_cmdline("BOOT_IMAGE=/vmlinuz ro quiet") is False

    def test_read_failure(self):
        with patch("latency_check.Path") as M:
            M.return_value.read_text.side_effect = PermissionError
            assert lc.check_isolcpus() is False


class TestHugepages:
    def _with_meminfo(self, content):
        with patch("latency_check.Path") as M:
            M.return_value.read_text.return_value = content
            return lc.check_hugepages()

    def test_pages_allocated(self):
        assert self._with_meminfo("MemTotal: 65536 kB\nHugePages_Total: 512\n") is True

    def test_zero_pages(self):
        assert self._with_meminfo("HugePages_Total: 0\n") is False

    def test_key_absent(self):
        assert self._with_meminfo("MemTotal: 65536 kB\n") is False

    def test_read_failure(self):
        with patch("latency_check.Path") as M:
            M.return_value.read_text.side_effect = PermissionError
            assert lc.check_hugepages() is False


class TestIrqbalance:
    def _with_status(self, stdout):
        r = MagicMock()
        r.stdout = stdout
        with patch("subprocess.run", return_value=r):
            return lc.check_irqbalance()

    def test_inactive(self):
        assert self._with_status("inactive\n") is True

    def test_active(self):
        assert self._with_status("active\n") is False

    def test_systemctl_missing(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert lc.check_irqbalance() is True


class TestCpuGovernor:
    def _mock_cpus(self, governors):
        mocks = []
        for g in governors:
            m = MagicMock()
            m.read_text.return_value = g
            mocks.append(m)
        return mocks

    def test_all_performance(self):
        with patch("latency_check.Path") as M:
            M.return_value.glob.return_value = self._mock_cpus(["performance", "performance"])
            assert lc.check_cpu_governor() is True

    def test_mixed_governors(self):
        with patch("latency_check.Path") as M:
            M.return_value.glob.return_value = self._mock_cpus(["performance", "powersave"])
            assert lc.check_cpu_governor() is False

    def test_no_cpufreq_in_container(self):
        with patch("latency_check.Path") as M:
            M.return_value.glob.return_value = []
            assert lc.check_cpu_governor() is True

    def test_read_failure_skips_cpu(self):
        m = MagicMock()
        m.read_text.side_effect = PermissionError
        with patch("latency_check.Path") as M:
            M.return_value.glob.return_value = [m]
            assert lc.check_cpu_governor() is True
