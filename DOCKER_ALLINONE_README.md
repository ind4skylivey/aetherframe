# 🐳 AetherFrame - Docker All-in-One

**Una única contenedor con todo lo necesario para ejecutar AetherFrame**

## ✨ Características

- ✅ **Un solo comando** para iniciar todo
- ✅ **Frontend + Backend** en un contenedor
- ✅ **Nginx** como proxy reverso
- ✅ **Supervisor** maneja todos los servicios
- ✅ **Auto-configuración** de bases de datos
- ✅ **Health checks** integrados
- ✅ **Logs centralizados**
- ✅ **Fácil de actualizar**

## 🚀 Quick Start

### 1. Iniciar AetherFrame

```bash
./start.sh
```

¡Eso es todo! El script:

1. Verifica que Docker esté instalado
2. Crea archivos de configuración
3. Construye el contenedor
4. Inicia todos los servicios
5. Espera a que esté listo

### 2. Acceder a la Aplicación

Abre tu navegador en:

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:3000/api/docs
- **MinIO Console**: http://localhost:9001

## 📋 Comandos Disponibles

```bash
./start.sh          # Iniciar AetherFrame
./start.sh stop     # Detener todos  los servicios
./start.sh restart  # Reiniciar
./start.sh logs     # Ver logs en tiempo real
./start.sh status   # Ver estado de servicios
./start.sh clean    # Limpiar todo (¡cuidado!)
./start.sh update   # Actualizar a última versión
```

## 🏗️ Arquitectura del Contenedor

```
┌─────────────────────────────────────────┐
│   AetherFrame All-in-One Container      │
│                                         │
│  ┌──────────┐  ┌──────────┐           │
│  │  Nginx   │  │ FastAPI  │           │
│  │  :80     │→ │  :8000   │           │
│  └──────────┘  └──────────┘           │
│                      ↓                  │
│              ┌──────────┐              │
│              │  Celery  │              │
│              │  Worker  │              │
│              └──────────┘              │
│                                         │
│  Managed by Supervisor                 │
└─────────────────────────────────────────┘
         ↓           ↓           ↓
   PostgreSQL     Redis       MinIO
   (Container)  (Container) (Container)
```

## 📦 Servicios Incluidos

| Servicio          | Puerto         | Descripción                      |
| ----------------- | -------------- | -------------------------------- |
| **Nginx**         | 80             | Proxy reverso + entrega frontend |
| **FastAPI**       | 8000 (interno) | API REST                         |
| **Celery Worker** | -              | Procesamiento asíncrono          |
| **PostgreSQL**    | 5432           | Base de datos principal          |
| **Redis**         | 6379           | Cache y cola de tareas           |
| **MinIO**         | 9000, 9001     | Almacenamiento de objetos        |

## ⚙️ Configuración

### Variables de Entorno (`.env`)

El script `start.sh` crea automáticamente un archivo `.env` con valores por defecto:

```bash
# Base de datos
POSTGRES_PASSWORD=aetherpass

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Puerto de la aplicación
AETHERFRAME_PORT=3000
```

**Para personalizar**, edita `.env` antes de ejecutar `./start.sh`

### Cambiar el Puerto

```bash
# Editar .env
AETHERFRAME_PORT=8080

# Reiniciar
./start.sh restart
```

Ahora la aplicación estará en http://localhost:8080

## 🔍 Solución de Problemas

### Ver Logs

```bash
# Logs de la aplicación principal
./start.sh logs

# Logs de un servicio específico
docker compose -f docker-compose.allinone.yml logs postgres
docker compose -f docker-compose.allinone.yml logs redis
```

### Verificar Estado de Servicios

```bash
./start.sh status
```

### Reiniciar Servicios

```bash
# Reiniciar todo
./start.sh restart

# Reiniciar solo un servicio
docker compose -f docker-compose.allinone.yml restart aetherframe
```

### Base de Datos No Responde

```bash
# Verificar salud de PostgreSQL
docker compose -f docker-compose.allinone.yml ps postgres

# Ver logs de PostgreSQL
docker compose -f docker-compose.allinone.yml logs postgres
```

### El Frontend No Carga

1. Verifica que nginx esté corriendo:

   ```bash
   docker exec aetherframe-app ps aux | grep nginx
   ```

2. Revisa logs de nginx:
   ```bash
   docker exec aetherframe-app cat /var/log/nginx/error.log
   ```

## 🎯 Uso Avanzado

### Ejecutar Comandos Dentro del Contenedor

```bash
# Shell interactivo
docker exec -it aetherframe-app /bin/bash

# Comando directo
docker exec aetherframe-app python /app/cli/main.py --help
```

### Analizar un Binario

```bash
# Copiar binario al contenedor
docker cp /path/to/malware.exe aetherframe-app:/app/samples/

# Ejecutar análisis
docker exec aetherframe-app \
  python /app/cli/main.py run /app/samples/malware.exe \
  --pipeline quicklook --wait
```

### Backup de Datos

```bash
# Backup de todas las bases de datos
docker compose -f docker-compose.allinone.yml exec postgres \
  pg_dumpall -U aether > backup.sql

# Restaurar
cat backup.sql | docker compose -f docker-compose.allinone.yml exec -T postgres \
  psql -U aether
```

## 🔄 Actualización

### Actualizar a Última Versión

```bash
./start.sh update
```

Esto:

1. Descarga el código más reciente (git pull)
2. Reconstruye el contenedor
3. Reinicia los servicios

### Actualización Manual

```bash
# Parar servicios
./start.sh stop

# Actualizar código
git pull

# Reconstruir y reiniciar
docker compose -f docker-compose.allinone.yml build --no-cache
docker compose -f docker-compose.allinone.yml up -d
```

## 🧹 Limpieza

### Limpiar Datos (¡CUIDADO!)

```bash
./start.sh clean
```

Esto eliminará:

- ❌ Todos los contenedores
- ❌ Todos los volúmenes (base de datos, redis, minio)
- ❌ Todos los análisis guardados

**Solo usa esto si quieres empezar de cero**

### Limpiar Solo Imágenes Viejas

```bash
docker image prune -f
```

## 📊 Monitoreo

### Health Checks

Todos los servicios tienen health checks configurados:

```bash
# Ver estado de salud
docker compose -f docker-compose.allinone.yml ps
```

Estados:

- `healthy` - ✅ Todo bien
- `starting` - ⏳ Iniciando
- `unhealthy` - ❌ Hay un problema

### Endpoint de Salud

```bash
curl http://localhost:3000/health
# Respuesta: healthy
```

## 🎓 Diferencias con Setup Manual

| Característica   | All-in-One            | Setup Manual          |
| ---------------- | --------------------- | --------------------- |
| **Instalación**  | Un comando            | Múltiples pasos       |
| **Servicios**    | 1 contenedor + 3 deps | 5+ contenedores       |
| **Port Exposed** | Solo 3000             | 8000, 3000, 5432, etc |
| **Nginx**        | ✅ Incluido           | ❌ No incluido        |
| **Proxy**        | ✅ Configurado        | Manual                |
| **Logs**         | Centralizados         | Dispersos             |
| **Updates**      | `./start.sh update`   | Manual rebuild        |

## 🎉 Ventajas

✅ **Simplicidad**: Un solo comando para todo
✅ **Portabilidad**: Funciona en cualquier sistema con Docker
✅ **Rapidez**: Configuración automática
✅ **Seguridad**: Menos puertos expuestos
✅ **Mantenibilidad**: Actualizaciones sencillas
✅ **Logs**: Centralizados y fáciles de acceder

## 📝 Notas

- **Persistencia**: Los datos se guardan en volúmenes Docker
- **Performance**: Similar al setup multi-contenedor
- **Escalabilidad**: No recomendado para producción de alta carga
- **Desarrollo**: Usa el setup manual para desarrollo activo

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `./start.sh logs`
2. Verifica el estado: `./start.sh status`
3. Intenta reiniciar: `./start.sh restart`
4. Como último recurso: `./start.sh clean` y `./start.sh`

---

**🚀 ¡Disfruta usando AetherFrame!**
