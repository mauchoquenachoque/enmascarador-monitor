from sqlalchemy.orm import Session

from app.models.benchmark_result import BenchmarkResult


class BenchmarkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, result: BenchmarkResult) -> BenchmarkResult:
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_all(self, skip: int = 0, limit: int = 100) -> list[BenchmarkResult]:
        return (
            self.db.query(BenchmarkResult)
            .order_by(BenchmarkResult.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_engine(self, engine: str) -> list[BenchmarkResult]:
        return (
            self.db.query(BenchmarkResult)
            .filter(BenchmarkResult.engine == engine)
            .all()
        )

    def get_by_algorithm(self, algorithm: str) -> list[BenchmarkResult]:
        return (
            self.db.query(BenchmarkResult)
            .filter(BenchmarkResult.algorithm == algorithm)
            .all()
        )

    def get_comparison_matrix(self) -> list[BenchmarkResult]:
        return self.db.query(BenchmarkResult).all()
