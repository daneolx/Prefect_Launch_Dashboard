from prefect import task, flow, get_run_logger
from prefect.states import Failed
from prefect.tasks import task_input_hash
import random
import subprocess
import asyncio

# Tarea 1: Extracción de datos con posible fallo y reintento
@task(retries=3, retry_delay_seconds=5)
def extract_data():
    logger = get_run_logger()
    logger.info("Extrayendo datos desde fuente externa...")
    
    # Simulación de fallo aleatorio
    if random.random() < 0.3:
        logger.error("Fallo en extracción. Reintentando...")
        raise Failed()
    
    return {"raw_data": [1, 2, 3, 4, 5]}

# Tarea 2: Transformación con caché para evitar procesamiento redundante
@task(cache_key_fn=task_input_hash)
def transform_data(data):
    logger = get_run_logger()
    logger.info("Transformando datos...")
    processed = [x * 2 for x in data["raw_data"]]
    return {"processed": processed}

# Tarea 3: Carga a base de datos (ejecución paralela)
@task(name="Cargar a Base de Datos")
async def load_to_db(data):
    logger = get_run_logger()
    logger.info(f"Cargando {data['processed']} a PostgreSQL...")
    await asyncio.sleep(2)  # Simulación de latencia
    return "Carga a DB exitosa"

# Tarea 4: Carga a API externa (ejecución paralela)
@task(name="Cargar a API")
async def load_to_api(data):
    logger = get_run_logger()
    logger.info(f"Enviando {data['processed']} a API REST...")
    await asyncio.sleep(2)
    return "Carga a API exitosa"

# Tarea 5: Ejecución de script externo (por ejemplo, validación con Bash)
@task
def run_validation_script():
    logger = get_run_logger()
    logger.info("Ejecutando script de validación externo...")
    result = subprocess.run(
        ["bash", "-c", "echo 'Validación completada: OK' && exit 0"],
        capture_output=True,
        text=True
    )
    logger.info(result.stdout)
    return result.returncode == 0

# Tarea 6: Notificación condicional
@task
def send_notification(result):
    logger = get_run_logger()
    logger.info(f"Notificando resultado: {result}")
    return "Notificación enviada"

# Flujo principal
@flow(name="Pipeline Complejo de Datos")
async def data_pipeline():
    # Extracción y transformación secuencial
    raw_data = extract_data()
    processed_data = transform_data(raw_data)

    # Ejecución paralela de cargas
    db_result, api_result = await asyncio.gather(
        load_to_db(processed_data),
        load_to_api(processed_data)
    )

    # Validación condicional
    validation_passed = run_validation_script()
    
    # Notificación solo si la validación fue exitosa
    if validation_passed:
        final_status = send_notification({"db": db_result, "api": api_result})
    else:
        final_status = "Validación fallida. No se envió notificación."
    
    return final_status

# Ejecución local
if __name__ == "__main__":
    asyncio.run(data_pipeline())