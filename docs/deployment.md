# Guía de Despliegue Gratuito

## Arquitectura de Despliegue

```
┌─────────────────┐     ┌──────────────────┐
│   Render Free   │     │  Supabase Free   │
│   (Backend)     │────▶│  (PostgreSQL)    │
│   Python 3.11   │     │  500MB gratis    │
└────────┬────────┘     └──────────────────┘
         │
         ▼
┌─────────────────┐
│  Frontend HTML  │
│  (servido por   │
│   FastAPI)      │
└─────────────────┘
```

---

## Paso 1: Preparar el Repositorio

### 1.1 Crear cuenta en GitHub
- Ve a https://github.com
- Crea un repositorio público: `masking-monitor`

### 1.2 Subir el código
```bash
cd /workspaces/enmascarador-monitor
git add -A
git commit -m "feat: proyecto completo listo para despliegue"
git remote add origin https://github.com/TU_USUARIO/masking-monitor.git
git push -u origin main
```

---

## Paso 2: Crear Base de Datos en Supabase (Gratis)

### 2.1 Crear proyecto
1. Ve a https://supabase.com
2. Crea cuenta con GitHub
3. Click "New Project"
4. Elige nombre: `masking-monitor`
5. Elige contraseña para la BD (guárdala)
6. Elige región: `East US (North Virginia)`
7. Click "Create project"

### 2.2 Obtener la URL de conexión
1. Ve a Settings → Database
2. Busca "Connection string" → URI
3. Copia algo como:
   ```
   postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

---

## Paso 3: Desplegar Backend en Render (Gratis)

### 3.1 Crear cuenta en Render
1. Ve a https://render.com
2. Click "Get Started for Free"
3. Inicia sesión con GitHub

### 3.2 Crear Web Service
1. Click "New +" → "Web Service"
2. Conecta tu repositorio `masking-monitor`
3. Configura:

| Campo | Valor |
|-------|-------|
| **Name** | `masking-monitor` |
| **Region** | `Oregon (US West)` |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:application --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

### 3.3 Configurar Variables de Entorno
En la sección "Environment Variables", agrega:

| Variable | Valor |
|----------|-------|
| `SECRET_KEY` | Genera uno con: `openssl rand -hex 32` |
| `DATABASE_URL` | La URL de Supabase del Paso 2 |
| `DEBUG` | `false` |
| `LOG_LEVEL` | `INFO` |
| `CORS_ORIGINS` | `["*"]` |

### 3.4 Desplegar
1. Click "Create Web Service"
2. Render empieza a compilar (tarda 2-5 minutos)
3. Cuando termine, verás la URL: `https://masking-monitor.onrender.com`

### 3.5 Verificar
```bash
# Health check
curl https://masking-monitor.onrender.com/health

# Login
curl -X POST https://masking-monitor.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'
```

---

## Paso 4: Acceder a la Aplicación

Abre en tu navegador:

```
https://masking-monitor.onrender.com/
```

Te redirige automáticamente al login.

**Credenciales:** `admin` / `Admin123!`

### URLs importantes:
| URL | Descripción |
|-----|-------------|
| `/` | Redirige al login |
| `/static/login.html` | Login |
| `/static/dashboard.html` | Dashboard |
| `/static/compare.html` | Comparador |
| `/static/benchmark.html` | Benchmark |
| `/static/reports.html` | Reportes |
| `/docs` | Swagger API |
| `/health` | Health check |

---

## Paso 5 (Opcional): Dominio Personalizado

### En Render:
1. Ve a tu Web Service → Settings
2. "Custom Domains"
3. Agrega tu dominio
4. Configura el DNS según las instrucciones

---

## Solución de Problemas

### El build falla
- Verifica que `Root Directory` sea `backend`
- Verifica que `requirements.txt` existe en `backend/`

### Error de base de datos
- Verifica que `DATABASE_URL` sea correcta
- Supabase usa puerto `6543` (pooler) o `5432` (directo)

### La app no arranca
- Revisa los logs en Render → Logs
- Verifica que `SECRET_KEY` esté configurado

### Cold start lento
- Render Free tiene cold start de ~30 segundos
- La primera petición después de inactividad es lenta
- Esto es normal en el plan gratuito

---

## Costo

| Servicio | Plan | Costo |
|----------|------|-------|
| Render | Free | $0/mes |
| Supabase | Free | $0/mes |
| GitHub | Free | $0/mes |
| **Total** | | **$0/mes** |

---

## Límites del Plan Gratis

### Render Free:
- 750 horas/mes de ejecución
- Cold start de ~30 segundos
- Se suspende después de 15 min de inactividad
- 512MB RAM

### Supabase Free:
- 500MB de almacenamiento
- 2GB de transferencia/mes
- 50,000 usuarios mensuales
