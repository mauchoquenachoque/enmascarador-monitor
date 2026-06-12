# API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Autenticación

Todos los endpoints protegidos requieren header:
```
Authorization: Bearer <access_token>
```

### POST /auth/login
Iniciar sesión y obtener tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "Admin123!"
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /auth/refresh
Renovar access token usando refresh token.

### POST /auth/logout
Revocar refresh token.

### GET /auth/me
Obtener información del usuario actual.

---

## Bases de Datos

### GET /databases/engines
Listar motores soportados.

### POST /databases/test
Probar conexión a una base de datos.

### POST /databases/schema
Obtener esquema de una base de datos.

### POST /databases/execute
Ejecutar query directa.

---

## Enmascaramiento

### GET /masking/algorithms
Listar algoritmos disponibles.

**Response:**
```json
{
  "algorithms": [
    {"name": "redaccion", "key": "redaccion", "reversible": false, "description": "...", "performance": "Muy rápido"},
    {"name": "hashing", "key": "hashing", "reversible": false, "description": "...", "performance": "Rápido"},
    {"name": "encriptacion", "key": "encriptacion", "reversible": true, "description": "...", "performance": "Moderado"},
    {"name": "fpe", "key": "fpe", "reversible": false, "description": "...", "performance": "Lento"}
  ]
}
```

### POST /masking/apply
Aplicar enmascaramiento a datos.

**Request:**
```json
{
  "data": [{"name": "Juan", "email": "juan@test.com"}],
  "rules": {"name": "redaccion", "email": "hashing"}
}
```

**Response:**
```json
{
  "masked_data": [{"name": "XXXX", "email": "a1b2c3d4e5f6..."}],
  "algorithm_used": ["redaccion", "hashing"],
  "rows_processed": 1,
  "masking_latency_ms": 0.045,
  "cpu_percent": 2.1,
  "ram_mb": 0.01
}
```

---

## Consultas

### POST /queries/run
Ejecutar consulta con enmascaramiento opcional.

### GET /queries/history
Historial de consultas del usuario.

---

## Benchmark

### POST /benchmarks/run
Ejecutar benchmark repetido.

**Request:**
```json
{
  "connection_id": "uuid",
  "table": "users",
  "algorithms": ["redaccion", "hashing", "encriptacion", "fpe"],
  "iterations": 10
}
```

### GET /benchmarks/history
Historial de benchmarks.

---

## Métricas

### GET /metrics/live
CPU, RAM, conexiones activas en tiempo real.

### GET /metrics/history?limit=100
Historial de métricas.

### GET /metrics/summary
Resumen estadístico.

### GET /metrics/export?format=csv
Exportar métricas en CSV o JSON.

---

## Dashboard

### GET /dashboard/stats
Estadísticas KPI para el dashboard.

---

## Observabilidad

### GET /health
Health check.

### GET /ready
Readiness check.
