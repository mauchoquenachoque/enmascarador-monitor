# Seguridad

## Autenticación

### JWT (JSON Web Tokens)
- Access Token: expira en 30 minutos (configurable)
- Refresh Token: expira en 7 días
- Algoritmo: HS256
- Claims: sub (username), role, exp, type

### Roles
| Rol | Permisos |
|-----|----------|
| admin | CRUD usuarios, todo acceso |
| analyst | Ejecutar consultas, benchmarks, masking |
| viewer | Ver dashboard, métricas, exportar |

### Contraseñas
- Hasheadas con bcrypt
- Mínimo 8 caracteres
- Nunca almacenadas en texto plano

## Protecciones Implementadas

### Rate Limiting
- 60 requests/minuto por IP (configurable)
- Middleware que rechaza con HTTP 429

### CORS
- Orígenes configurables via `CORS_ORIGINS`
- Credentials habilitados

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Input Validation
- Pydantic v2 para validación de todos los inputs
- Regex patterns para campos como engine, role
- Límites de longitud en strings

### SQL Injection Protection
- SQLAlchemy ORM con queries parametrizadas
- Nunca string formatting directo en queries del sistema

### Secrets Management
- Variables de entorno via `.env`
- `pydantic-settings` para carga automática
- `.gitignore` excluye `.env` y `.keyfile`

## Auditoría

Cada acción relevante se registra en `audit_logs`:
- usuario que ejecutó
- acción realizada
- recurso afectado
- timestamp
- IP address
- overhead percent (si aplica)

## Fernet Key

La clave Fernet para cifrado AES se persiste en `.keyfile`:
- Generada automáticamente si no existe
- Permisos restrictivos (0o600 en Unix)
- Nunca se incluye en el repositorio
