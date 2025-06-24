

## ✅ Resumen

Con esta guía puedes:

1. Instalar Prefect y levantar su servidor en RHEL.
2. Crear y mantener work pools y worker processes.
3. Desplegar flujos en pools con schedules específicos.
4. Administrar infraestructuras con comandos CLI claros y directos.
5. Usar solo la primera vez en la instalacion del enviroment python3 -m venv ~/prefect-env
---

# 🖥️ Guía de instalación y operación de Prefect en RHEL

## 1. Crear entorno virtual e instalar Prefect

```bash
cd /opt/Prefect_io/
source ~/prefect-env/bin/activate

pip install prefect
prefect version
```

---

## 2. Inicializar y arrancar el servidor Prefect

```bash
# Opción básica (usa puerto local)
prefect server start

# Opción pública (accesible desde la LAN)
sudo firewall-cmd --permanent --add-port=4200/tcp
sudo firewall-cmd --reload

prefect server start --host 0.0.0.0 --port 4200
```

### ⏳ En ejecución en segundo plano

```bash
nohup prefect server start --host 0.0.0.0 --port 4200 \
  > ~/prefect-server.log 2>&1 &
disown
```

---

## 3. Configurar conexión a base de datos PostgreSQL

Anterior a arrancar el servidor o exporta la variable en tu sesión:

```bash
export PREFECT_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/prefect_server"
```

Luego inicia el servidor:

```bash
prefect server start --host 0.0.0.0 --port 4200
```

Validar salud del servidor API:

```bash
curl http://127.0.0.1:4200/api/health
```

---

## 4. Configurar CLI para apuntar al servidor local

```bash
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

---

## 5. Crear y ejecutar **work pools**

### Crear pools vía CLI (solo si no existen)

```bash
prefect work-pool create pool-monitoreo-AIJC --type process
prefect work-pool create pool-monitoreo-GDR --type process
```

### Iniciar un worker (ejemplo)

```bash
prefect worker start --pool pool-monitoreo-AIJC
prefect worker start --pool pool-monitoreo-GDR
```

### Ejecutar worker en segundo plano

```bash
nohup prefect worker start --pool pool-monitoreo-GDR \
  > ~/prefect-worker.log 2>&1 &
disown
```

---

## 6. Desplegar flujos

### FLujo ETL (SQL Server → PostgreSQL)

```bash
prefect deploy job_ETL_SQLserver_to_PostgreSQL.py:flujo_principal \
  -n "aijc-proceso_ETL_SQLserver_to_PostgreSQL" \
  --pool pool-monitoreo-AIJC \
  --cron "2 5 * * *" --timezone America/Lima
```

### Flujo creación de tablas de monitoreo

```bash
prefect deploy job_creacion_tablas_monitoreo.py:flujo_principal \
  -n "aijc-proceso-creacion-tablas-monitoreo" \
  --pool pool-monitoreo-AIJC --interval 600
```

---

## 7. Uso de `prefect.yaml`

```bash
cd /opt/Prefect_io/
prefect init
# Edita prefect.yaml con tus infraestructura y flujos
prefect deploy job_Generar_Indicadores_Mensual:flujo_principal \
  -n "GDR-Genera-Indicadores-Mensual" \
  --pool pool-monitoreo-GDR --interval 3600
```

### Redeploy de todos los deployments

```bash
prefect deploy --all
```

---

## 8. Comandos útiles para administrar infraestructura Prefect

### 🟢 Work Pools

* Listar todos los pools:

  ```bash
  prefect work-pool ls
  ```

  ([reddit.com][1], [docs-3.prefect.io][2], [reddit.com][3], [docs-3.prefect.io][4])

* Ver detalles de un pool:

  ```bash
  prefect work-pool inspect pool-monitoreo-GDR
  ```

  ([docs-2.prefect.io][5])

* Previsualizar próximos runs:

  ```bash
  prefect work-pool preview pool-monitoreo-GDR --hours 12
  ```

  ([docs-3.prefect.io][2])

### 🚀 Deployments

* Listar todos los deployments:

  ```bash
  prefect deployment ls
  ```

  ([docs.prefect.io][6])

* Filtrar deployments por flujo:

  ```bash
  prefect deployment ls job_Generar_Indicadores_Mensual
  ```

* Ver detalles específicos:

  ```bash
  prefect deployment inspect job_Generar_Indicadores_Mensual/GDR-Genera-Indicadores-Mensual
  ```

---


