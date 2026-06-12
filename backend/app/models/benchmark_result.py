import uuid

from sqlalchemy import Column, Float, Integer, String

from app.models.base import Base, TimestampMixin


class BenchmarkResult(Base, TimestampMixin):
    __tablename__ = "benchmark_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    engine = Column(String(50), nullable=False)
    algorithm = Column(String(50), nullable=False)
    iterations = Column(Integer, nullable=False)
    avg_db_latency_ms = Column(Float, default=0.0)
    avg_masking_latency_ms = Column(Float, default=0.0)
    avg_total_latency_ms = Column(Float, default=0.0)
    avg_overhead_percent = Column(Float, default=0.0)
    avg_cpu_percent = Column(Float, default=0.0)
    avg_ram_mb = Column(Float, default=0.0)
    throughput_qps = Column(Float, default=0.0)
    p50_ms = Column(Float, default=0.0)
    p95_ms = Column(Float, default=0.0)
    p99_ms = Column(Float, default=0.0)

    def __repr__(self) -> str:
        return f"<Benchmark {self.engine}/{self.algorithm} iters={self.iterations}>"
