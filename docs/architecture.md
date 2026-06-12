# Arquitectura del Sistema

## Visión General

La plataforma sigue **Clean Architecture** con separación clara de responsabilidades:

```
┌─────────────────────────────────────────────┐
│                API Layer                     │
│         (FastAPI Endpoints)                  │
├─────────────────────────────────────────────┤
│             Service Layer                    │
│        (Business Logic)                      │
├─────────────────────────────────────────────┤
│           Repository Layer                   │
│         (Data Access)                        │
├─────────────────────────────────────────────┤
│            Model Layer                       │
│      (SQLAlchemy ORM)                        │
└─────────────────────────────────────────────┘
```

## Principios Aplicados

### SOLID
- **S**: Cada módulo tiene una sola responsabilidad
- **O**: MaskingFactory extensible sin modificar código existente
- **L**: BaseDatabase puede ser sustituido por cualquier engine
- **I**: Interfaces segregadas (BaseDatabase, MaskingStrategy)
- **D**: Dependencias inyectadas via FastAPI Depends

### Patrones

| Patrón | Implementación |
|--------|---------------|
| Factory | DatabaseFactory, MaskingFactory |
| Strategy | MaskingStrategy (redacción, hashing, AES, FPE) |
| Repository | UserRepository, ConnectionRepository, etc. |
| Dependency Injection | FastAPI Depends() |

## Flujo de Datos

### Consulta con Enmascaramiento
```
Client → API Endpoint → Service → DatabaseFactory.create()
                                      ↓
                              Engine.execute_query()
                                      ↓
                              Raw Data returned
                                      ↓
                        MaskingFactory.apply_masking()
                                      ↓
                        MetricsCollector.measure()
                                      ↓
                        Response with metrics
```

## Seguridad

- JWT con access + refresh tokens
- bcrypt para hashing de contraseñas
- Rate limiting por IP
- CORS configurable
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Variables de entorno para secrets (nunca hardcodeados)
