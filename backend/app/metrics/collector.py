import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import psutil

from app.core.logging import get_logger

logger = get_logger("metrics")


@dataclass
class MeasurementResult:
    db_latency_ns: int = 0
    masking_latency_ns: int = 0
    total_latency_ns: int = 0
    db_latency_ms: float = 0.0
    masking_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    overhead_percent: float = 0.0
    cpu_percent: float = 0.0
    ram_mb: float = 0.0
    rows_processed: int = 0
    engine: str = ""
    algorithm: str = ""
    throughput_qps: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "db_latency_ms": round(self.db_latency_ms, 3),
            "masking_latency_ms": round(self.masking_latency_ms, 3),
            "total_latency_ms": round(self.total_latency_ms, 3),
            "overhead_percent": round(self.overhead_percent, 2),
            "cpu_percent": round(self.cpu_percent, 2),
            "ram_mb": round(self.ram_mb, 2),
            "rows_processed": self.rows_processed,
            "engine": self.engine,
            "algorithm": self.algorithm,
            "throughput_qps": round(self.throughput_qps, 2),
        }


class MetricsCollector:
    def __init__(self) -> None:
        self._process = psutil.Process()
        self._history: list[dict[str, Any]] = []

    def get_cpu_percent(self) -> float:
        return self._process.cpu_percent(interval=None)

    def get_ram_usage(self) -> tuple[float, float]:
        mem = self._process.memory_info()
        mb = mem.rss / (1024 * 1024)
        percent = self._process.memory_percent()
        return mb, percent

    def measure_query(
        self,
        db_func: Callable[[], list[dict[str, Any]]],
        masking_func: Callable[[list[dict[str, Any]]], list[dict[str, Any]]] | None = None,
        engine: str = "",
        algorithm: str = "",
    ) -> MeasurementResult:
        result = MeasurementResult(engine=engine, algorithm=algorithm)

        cpu_before = self.get_cpu_percent()
        ram_before, _ = self.get_ram_usage()

        start_db = time.perf_counter_ns()
        raw_data = db_func()
        end_db = time.perf_counter_ns()

        result.db_latency_ns = end_db - start_db
        result.db_latency_ms = result.db_latency_ns / 1_000_000.0
        result.rows_processed = len(raw_data) if raw_data else 0

        if masking_func and raw_data:
            start_mask = time.perf_counter_ns()
            masking_func(raw_data)
            end_mask = time.perf_counter_ns()

            result.masking_latency_ns = end_mask - start_mask
            result.masking_latency_ms = result.masking_latency_ns / 1_000_000.0

        result.total_latency_ns = result.db_latency_ns + result.masking_latency_ns
        result.total_latency_ms = result.total_latency_ns / 1_000_000.0

        if result.db_latency_ms > 0:
            result.overhead_percent = (result.masking_latency_ms / result.db_latency_ms) * 100

        cpu_after = self.get_cpu_percent()
        ram_after, _ = self.get_ram_usage()
        result.cpu_percent = max(cpu_after - cpu_before, 0)
        result.ram_mb = max(ram_after - ram_before, 0)

        if result.total_latency_ms > 0:
            result.throughput_qps = 1000.0 / result.total_latency_ms

        self._history.append(result.to_dict())
        return result

    def get_history(self) -> list[dict[str, Any]]:
        return self._history.copy()

    def get_summary(self) -> dict[str, Any]:
        if not self._history:
            return {"count": 0}

        db_latencies = [m["db_latency_ms"] for m in self._history]
        mask_latencies = [m["masking_latency_ms"] for m in self._history]
        overheads = [m["overhead_percent"] for m in self._history]
        cpus = [m["cpu_percent"] for m in self._history]
        rams = [m["ram_mb"] for m in self._history]

        return {
            "count": len(self._history),
            "avg_db_latency_ms": round(sum(db_latencies) / len(db_latencies), 3),
            "avg_masking_latency_ms": round(sum(mask_latencies) / len(mask_latencies), 3),
            "avg_overhead_percent": round(sum(overheads) / len(overheads), 2),
            "avg_cpu_percent": round(sum(cpus) / len(cpus), 2),
            "avg_ram_mb": round(sum(rams) / len(rams), 2),
            "min_db_latency_ms": round(min(db_latencies), 3),
            "max_db_latency_ms": round(max(db_latencies), 3),
        }

    def clear(self) -> None:
        self._history.clear()


collector = MetricsCollector()
