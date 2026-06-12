import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.auth.dependencies import require_viewer
from app.metrics.collector import collector
from app.schemas.metric import LiveMetrics

router = APIRouter(prefix="/metrics", tags=["Métricas"])


@router.get("/live", response_model=LiveMetrics)
def get_live_metrics(
    _: dict = Depends(require_viewer),
) -> LiveMetrics:
    import psutil

    process = psutil.Process()
    cpu = process.cpu_percent(interval=0.1)
    ram_mb = process.memory_info().rss / (1024 * 1024)
    ram_percent = process.memory_percent()

    return LiveMetrics(
        cpu_percent=round(cpu, 2),
        ram_mb=round(ram_mb, 2),
        ram_percent=round(ram_percent, 2),
        active_connections=1,
        total_queries=len(collector.get_history()),
    )


@router.get("/history")
def get_metrics_history(
    limit: int = Query(default=100, ge=1, le=1000),
    _: dict = Depends(require_viewer),
) -> list[dict[str, Any]]:
    return collector.get_history()[-limit:]


@router.get("/summary")
def get_metrics_summary(
    _: dict = Depends(require_viewer),
) -> dict[str, Any]:
    return collector.get_summary()


@router.get("/export")
def export_metrics(
    fmt: str = Query(default="json", pattern="^(json|csv)$"),
    _: dict = Depends(require_viewer),
) -> Any:
    history = collector.get_history()

    if fmt == "csv":
        if not history:
            return StreamingResponse(
                io.StringIO("No data"),
                media_type="text/csv",
            )
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=metrics.csv"},
        )

    return history
