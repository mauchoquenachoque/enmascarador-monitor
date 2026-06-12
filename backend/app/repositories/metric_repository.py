from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.metric import Metric


class MetricRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, metric: Metric) -> Metric:
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_by_type(self, metric_type: str, skip: int = 0, limit: int = 100) -> list[Metric]:
        return (
            self.db.query(Metric)
            .filter(Metric.metric_type == metric_type)
            .order_by(Metric.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_summary(self, metric_type: str) -> dict:
        result = (
            self.db.query(
                func.count(Metric.id).label("count"),
                func.avg(Metric.value).label("avg"),
                func.min(Metric.value).label("min_val"),
                func.max(Metric.value).label("max_val"),
            )
            .filter(Metric.metric_type == metric_type)
            .first()
        )
        if result and result.count:
            return {
                "metric_type": metric_type,
                "count": result.count,
                "avg": round(float(result.avg), 3),
                "min_val": round(float(result.min_val), 3),
                "max_val": round(float(result.max_val), 3),
            }
        return {"metric_type": metric_type, "count": 0, "avg": 0, "min_val": 0, "max_val": 0}

    def get_all(self, skip: int = 0, limit: int = 500) -> list[Metric]:
        return (
            self.db.query(Metric).order_by(Metric.created_at.desc()).offset(skip).limit(limit).all()
        )
