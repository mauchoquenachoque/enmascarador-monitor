# Metodología de Benchmark

## Objetivo

Medir cuantitativamente el "impuesto de rendimiento" (overhead) que cada algoritmo de enmascaramiento introduce en las consultas a bases de datos.

## Métricas Capturadas

### Latencia DB (ms)
Tiempo puro de ejecución de la consulta en la base de datos.
Medido con `time.perf_counter_ns()` antes y después de `execute_query()`.

### Latencia Masking (ms)
Tiempo de procesamiento del algoritmo de enmascaramiento.
Medido con `time.perf_counter_ns()` antes y después de `apply_masking()`.

### Latencia Total (ms)
Suma de latencia DB + latencia masking.

### Overhead % (porcentaje de sobrecosto)
```
overhead_percent = (masking_time / db_time) * 100
```

### CPU %
Uso de CPU durante el proceso, medido con `psutil.Process().cpu_percent()`.

### RAM MB
Consumo de memoria durante el proceso, medido con `psutil.Process().memory_info()`.

### Throughput (QPS)
Consultas por segundo: `1000 / total_latency_ms`

### Percentiles
- **P50**: Latencia mediana
- **P95**: 95% de las consultas son más rápidas
- **P99**: 99% de las consultas son más rápidas

## Algoritmos Evaluados

| Algoritmo | Tipo | Reversible | Complejidad |
|-----------|------|------------|-------------|
| Redacción | Sustitución | No | O(n) |
| SHA-256 | Hash | No | O(n) |
| AES/Fernet | Cifrado simétrico | Sí | O(n) |
| FPE | Cifrado preservando formato | No | O(n × 5000) |

## Protocolo de Prueba

1. Conectar a la base de datos objetivo
2. Ejecutar consulta base (sin masking) para medir latencia DB
3. Para cada algoritmo:
   - Ejecutar N iteraciones
   - Aplicar masking a cada resultado
   - Capturar métricas en cada iteración
4. Calcular estadísticas: avg, min, max, P50, P95, P99
5. Generar reporte comparativo

## Interpretación

- **Overhead < 10%**: Impacto mínimo, algoritmo viable en producción
- **Overhead 10-50%**: Impacto moderado, evaluar trade-off seguridad/rendimiento
- **Overhead > 50%**: Impacto alto, considerar optimización o algoritmo alternativo
