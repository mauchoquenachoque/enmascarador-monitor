from fastapi import APIRouter, Depends

from app.auth.dependencies import require_analyst, require_viewer
from app.masking.factory import MaskingFactory
from app.schemas.masking import (
    AlgorithmInfo,
    AlgorithmListResponse,
    MaskingApplyRequest,
    MaskingApplyResponse,
)

router = APIRouter(prefix="/masking", tags=["Enmascaramiento"])


@router.get("/algorithms", response_model=AlgorithmListResponse)
def list_algorithms(
    _: dict = Depends(require_viewer),
) -> AlgorithmListResponse:
    descriptions = {
        "redaccion": {
            "description": "Reemplaza cada carácter con 'X'. Irreversible.",
            "performance": "Muy rápido",
        },
        "hashing": {
            "description": "Hash SHA-256 truncado a 16 caracteres. Irreversible.",
            "performance": "Rápido",
        },
        "encriptacion": {
            "description": "Cifrado simétrico AES con Fernet. Reversible con clave.",
            "performance": "Moderado",
        },
        "fpe": {
            "description": "Format Preserving Encryption. Conserva longitud y formato.",
            "performance": "Lento (5000 iteraciones SHA-256)",
        },
    }

    algorithms = []
    for info in MaskingFactory.available():
        key = info["key"]
        desc = descriptions.get(key, {"description": "", "performance": ""})
        algorithms.append(
            AlgorithmInfo(
                name=info["name"],
                key=key,
                reversible=info["reversible"],
                description=desc["description"],
                performance=desc["performance"],
            )
        )
    return AlgorithmListResponse(algorithms=algorithms)


@router.post("/apply", response_model=MaskingApplyResponse)
def apply_masking(
    data: MaskingApplyRequest,
    _: dict = Depends(require_analyst),
) -> MaskingApplyResponse:
    import time

    import psutil

    process = psutil.Process()
    cpu_before = process.cpu_percent(interval=None)
    ram_before = process.memory_info().rss / (1024 * 1024)

    start = time.perf_counter_ns()
    masked_data, algorithms = MaskingFactory.apply_masking(data.data, data.rules)
    end = time.perf_counter_ns()

    cpu_after = process.cpu_percent(interval=None)
    ram_after = process.memory_info().rss / (1024 * 1024)

    latency_ms = (end - start) / 1_000_000

    return MaskingApplyResponse(
        masked_data=masked_data,
        algorithm_used=algorithms,
        rows_processed=len(data.data),
        masking_latency_ms=round(latency_ms, 3),
        cpu_percent=round(max(cpu_after - cpu_before, 0), 2),
        ram_mb=round(max(ram_after - ram_before, 0), 2),
    )
