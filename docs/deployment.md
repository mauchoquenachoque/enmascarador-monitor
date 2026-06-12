# Guía de Despliegue

## Opción 1: Render (Backend) + Cloudflare Pages (Frontend)

### Backend en Render Free

1. Crear cuenta en [render.com](https://render.com)
2. Conectar repositorio de GitHub
3. Crear nuevo **Web Service**
4. Configurar:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
5. Variables de entorno:
   ```
   SECRET_KEY=<generar-con-openssl-rand-hex-32>
   DATABASE_URL=<supabase-postgresql-url>
   DEBUG=false
   LOG_LEVEL=INFO
   ```

### Frontend en Cloudflare Pages

1. Crear cuenta en [Cloudflare Pages](https://pages.cloudflare.com)
2. Conectar repositorio de GitHub
3. Configurar:
   - **Framework**: None
   - **Build command**: (vacío)
   - **Output directory**: `frontend`
4. Actualizar `frontend/js/api.js` con la URL del backend en Render

### Base de Datos en Supabase

1. Crear proyecto en [supabase.com](https://supabase.com)
2. Ir a Settings > Database
3. Copiar la Connection String (URI)
4. Configurar como `DATABASE_URL` en Render

---

## Opción 2: Docker Compose (VPS)

```bash
# Clonar
git clone <repo-url>
cd masking-monitor

# Configurar
cp backend/.env.example backend/.env
# Editar backend/.env

# Desplegar
docker-compose -f docker-compose.prod.yml up -d --build

# Verificar
curl http://localhost:8000/health
```

---

## Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| SECRET_KEY | Clave JWT | openssl rand -hex 32 |
| DATABASE_URL | URL de BD interna | sqlite:///./local_monitor.db |
| DEBUG | Modo debug | false |
| LOG_LEVEL | Nivel de log | INFO |
| CORS_ORIGINS | Orígenes CORS permitidos | ["https://tudominio.com"] |
| RATE_LIMIT_PER_MINUTE | Límite de requests | 60 |
