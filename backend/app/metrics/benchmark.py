import statistics
import time
from typing import Any, Callable

from app.core.logging import get_logger
from app.metrics.collector import MetricsCollector, MeasurementResult

logger = get_logger("benchmark")


class BenchmarkEngine:
    def __init__(self, collector: MetricsCollector) -> None:
        self.collector = collector

    def run_benchmark(
        self,
        db_func: Callable[[], list[dict[str, Any]]],
        masking_func: Callable[[list[dict[str, Any]]], list[dict[str, Any]]] | None,
        engine: str,
        algorithm: str,
        iterations: int = 10,
    ) -> dict[str, Any]:
        results: list[MeasurementResult] = []

        logger.info(
            "benchmark_started",
            engine=engine,
            algorithm=algorithm,
            iterations=iterations,
        )

        for i in range(iterations):
            result = self.collector.measure_query(
                db_func=db_func,
                masking_func=masking_func,
                engine=engine,
                algorithm=algorithm,
            )
            results.append(result)

        total_latencies = [r.total_latency_ms for r in results]
        total_latencies_sorted = sorted(total_latencies)

        p50_idx = int(len(total_latencies_sorted) * 0.5)
        p95_idx = int(len(total_latencies_sorted) * 0.95)
        p99_idx = int(len(total_latencies_sorted) * 0.99)

        summary = {
            "engine": engine,
            "algorithm": algorithm,
            "iterations": iterations,
            "avg_db_latency_ms": round(
                statistics.mean([r.db_latency_ms for r in results]), 3
            ),
            "avg_masking_latency_ms": round(
                statistics.mean([r.masking_latency_ms for r in results]), 3
            ),
            "avg_total_latency_ms": round(
                statistics.mean(total_latencies), 3
            ),
            "avg_overhead_percent": round(
                statistics.mean([r.overhead_percent for r in results]), 2
            ),
            "avg_cpu_percent": round(
                statistics.mean([r.cpu_percent for r in results]), 2
            ),
            "avg_ram_mb": round(
                statistics.mean([r.ram_mb for r in results]), 2
            ),
            "throughput_qps": round(
                statistics.mean([r.throughput_qps for r in results]), 2
            ),
            "p50_ms": round(total_latencies_sorted[p50_idx], 3),
            "p95_ms": round(total_latencies_sorted[min(p95_idx, len(total_latencies_sorted) - 1)], 3),
            "p99_ms": round(total_latencies_sorted[min(p99_idx, len(total_latencies_sorted) - 1)], 3),
            "min_latency_ms": round(min(total_latencies), 3),
            "max_latency_ms": round(max(total_latencies), 3),
            "std_dev_ms": round(
                statistics.stdev(total_latencies) if len(total_latencies) > 1 else 0, 3
            ),
        }

        individual = [
            {
                "iteration": i + 1,
                "db_latency_ms": round(r.db_latency_ms, 3),
                "masking_latency_ms": round(r.masking_latency_ms, 3),
                "total_latency_ms": round(r.total_latency_ms, 3),
                "overhead_percent": round(r.overhead_percent, 2),
                "cpu_percent": round(r.cpu_percent, 2),
                "ram_mb": round(r.ram_mb, 2),
            }
            for i, r in enumerate(results)
        ]

        logger.info(
            "benchmark_completed",
            engine=engine,
            algorithm=algorithm,
            avg_latency=summary["avg_total_latency_ms"],
        )

        return {
            "summary": summary,
            "individual": individual,
            "total_duration_ms": round(sum(total_latencies), 3),
        }
