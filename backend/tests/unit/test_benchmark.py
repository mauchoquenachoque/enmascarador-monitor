from app.metrics.benchmark import BenchmarkEngine
from app.metrics.collector import MetricsCollector


class TestBenchmarkEngine:
    def test_run_benchmark(self):
        collector = MetricsCollector()
        engine = BenchmarkEngine(collector)

        def mock_db():
            return [{"id": 1, "name": "test"}]

        def mock_mask(data):
            return [{"id": 1, "name": "XXXX"}]

        result = engine.run_benchmark(
            db_func=mock_db,
            masking_func=mock_mask,
            engine="sqlite",
            algorithm="redaccion",
            iterations=5,
        )

        assert "summary" in result
        assert "individual" in result
        assert result["summary"]["iterations"] == 5
        assert result["summary"]["engine"] == "sqlite"
        assert result["summary"]["algorithm"] == "redaccion"
        assert len(result["individual"]) == 5
        assert result["total_duration_ms"] >= 0

    def test_benchmark_percentiles(self):
        collector = MetricsCollector()
        engine = BenchmarkEngine(collector)

        def mock_db():
            return [{"id": 1}]

        result = engine.run_benchmark(
            db_func=mock_db,
            masking_func=None,
            engine="sqlite",
            algorithm="none",
            iterations=10,
        )

        summary = result["summary"]
        assert "p50_ms" in summary
        assert "p95_ms" in summary
        assert "p99_ms" in summary
        assert summary["p50_ms"] <= summary["p95_ms"]

    def test_benchmark_without_masking(self):
        collector = MetricsCollector()
        engine = BenchmarkEngine(collector)

        def mock_db():
            return [{"id": 1}]

        result = engine.run_benchmark(
            db_func=mock_db,
            masking_func=None,
            engine="sqlite",
            algorithm="none",
            iterations=3,
        )

        assert result["summary"]["avg_masking_latency_ms"] == 0
