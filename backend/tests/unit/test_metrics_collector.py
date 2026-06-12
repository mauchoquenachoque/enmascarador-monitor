from app.metrics.collector import MeasurementResult, MetricsCollector


class TestMetricsCollector:
    def test_collector_initializes(self):
        c = MetricsCollector()
        assert c.get_history() == []

    def test_measure_query_returns_result(self):
        c = MetricsCollector()

        def mock_db():
            return [{"id": 1, "name": "test"}]

        result = c.measure_query(db_func=mock_db, engine="sqlite", algorithm="none")
        assert isinstance(result, MeasurementResult)
        assert result.rows_processed == 1
        assert result.db_latency_ms >= 0
        assert result.engine == "sqlite"

    def test_measure_with_masking(self):
        c = MetricsCollector()

        def mock_db():
            return [{"id": 1, "name": "Juan"}]

        def mock_mask(data):
            return [{"id": 1, "name": "XXXX"}]

        result = c.measure_query(
            db_func=mock_db,
            masking_func=mock_mask,
            engine="sqlite",
            algorithm="redaccion",
        )
        assert result.masking_latency_ms >= 0
        assert result.total_latency_ms >= result.db_latency_ms

    def test_overhead_calculation(self):
        c = MetricsCollector()

        def mock_db():
            return [{"id": i} for i in range(100)]

        def slow_mask(data):
            import time

            time.sleep(0.001)
            return data

        result = c.measure_query(
            db_func=mock_db,
            masking_func=slow_mask,
            engine="sqlite",
            algorithm="test",
        )
        assert result.overhead_percent >= 0

    def test_history_accumulates(self):
        c = MetricsCollector()

        def mock_db():
            return []

        c.measure_query(db_func=mock_db, engine="sqlite")
        c.measure_query(db_func=mock_db, engine="sqlite")
        assert len(c.get_history()) == 2

    def test_summary_empty(self):
        c = MetricsCollector()
        summary = c.get_summary()
        assert summary["count"] == 0

    def test_summary_with_data(self):
        c = MetricsCollector()

        def mock_db():
            return [{"id": 1}]

        c.measure_query(db_func=mock_db, engine="sqlite")
        summary = c.get_summary()
        assert summary["count"] == 1
        assert "avg_db_latency_ms" in summary

    def test_clear_history(self):
        c = MetricsCollector()

        def mock_db():
            return []

        c.measure_query(db_func=mock_db)
        c.clear()
        assert len(c.get_history()) == 0

    def test_to_dict(self):
        m = MeasurementResult(
            db_latency_ms=1.5,
            masking_latency_ms=0.5,
            total_latency_ms=2.0,
            overhead_percent=33.33,
            rows_processed=10,
        )
        d = m.to_dict()
        assert d["db_latency_ms"] == 1.5
        assert d["overhead_percent"] == 33.33
        assert d["rows_processed"] == 10
