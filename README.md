# MCASB Data Pipeline
### Pipeline de datos bancarios - Bolsa de valores USA

Pipeline end-to-end que extrae, integra, valida y transforma datos financieros de bancos que cotizan en la bolsa de Estados Unidos, utilizando datos de Yahoo Finance (2024-2025).

---

## Arquitectura

<img width="4404" height="3136" alt="image" src="https://github.com/user-attachments/assets/fbf1b00b-d048-4b8e-adc9-c8fb03a30d6c" />


---

## Tecnologías utilizadas

| Herramienta | Función | Puerto |
|---|---|---|
| Python + Yahoo Finance| Extracción de datos del API | - |
| PostgreSQL 15 | Landing zone (datos crudos) | 5432 |
| ClickHouse 23.8 | Warehouse OLAP (datos curados) | 8123 |
| dbt | Validación y transformación | - |
| Apache Airflow 2.7 | Orquestación del pipeline | 8080 |
| Docker Compose | Contenedorización de servicios | - |

---

## Datos extraídos

Se procesan **20 bancos**: JPM, BAC, WFC, C, GS, MS, USB, PNC, TFC, COF, BK, STT, FITB, HBAN, MTB, KEY, RF, CFG, ZION, ALLY.

Para cada banco se extraen 5 conjuntos de datos:

1. **Información básica**: industria, sector, empleados, ubicación, website
2. **Precios diarios**: open, high, low, close, volume (~10,000 registros)
3. **Fundamentales**: assets, debt, invested capital, shares issued
4. **Tenedores institucionales**: holder, shares, value (200 registros)
5. **Calificaciones**: upgrades/downgrades de analistas (~1,900 registros)

---

## Estructura del proyecto

## Datos extraídos (2024-2025)

Se procesan 20 bancos: JPM, BAC, WFC, C, GS, MS, USB, PNC, TFC, COF, BK, STT, FITB, HBAN, MTB, KEY, RF, CFG, ZION, ALLY.

Para cada banco se extraen 5 conjuntos de datos:

1. **Información básica**: industria, sector, empleados, ubicación, website
2. **Precios diarios**: open, high, low, close, volume
3. **Fundamentales**: assets, debt, invested capital, shares issued
4. **Tenedores institucionales**: holder, shares, value
5. **Calificaciones**: upgrades, downgrades de analistas


## Cómo ejecutar el proyecto

### Prerequisitos
- Docker Desktop instalado
- Git instalado

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/imazcona/MCAsb-Pipeline.git
cd MCAsb-Pipeline
```

### Paso 2: Crear archivo de variables de entorno
```bash
cp .env.example .env
```

### Paso 3: Levantar los servicios con Docker
```bash
docker compose up -d
```

### Paso 4: Verificar que los contenedores están corriendo
```bash
docker compose ps
```
Debes ver 3 contenedores: `mcasb_landing_zone`, `mcasb_warehouse`, `mcasb_airflow`.

### Paso 5: Instalar dependencias Python
```bash
pip install yfinance pandas sqlalchemy psycopg2-binary clickhouse-driver dbt-clickhouse
```

### Paso 6: Ejecutar la extracción de datos
```bash
python 01_extraction/src/main.py
```
Este proceso extrae datos de 20 bancos desde Yahoo Finance y los carga en PostgreSQL.

### Paso 7: Integrar datos a ClickHouse
```bash
python 04_integration/pg_to_clickhouse.py
```

### Paso 8: Ejecutar transformaciones y validaciones con dbt
```bash
cd 05_transformation
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### Paso 9: Acceder a Airflow
- URL: http://localhost:8080
- Usuario: `admin`
- Contraseña: `admin`

---

## Screenshots del entorno

### Airflow UI - DAG del pipeline
![aiflow_ui](https://github.com/user-attachments/assets/897c8d38-cbf3-4e03-9b39-1babdb35e456)


### PostgreSQL - Datos en el landing zone
<img width="451" height="225" alt="postgresdatos" src="https://github.com/user-attachments/assets/d99e4015-90d5-424b-a339-d011f8c5f993" />


### ClickHouse - Tabla resumen mensual
<img width="519" height="217" alt="clickhouse_resumen" src="https://github.com/user-attachments/assets/e479be97-1f1e-4bd5-bad2-9594955fc508" />


### dbt - Tests de validación pasando
<img width="779" height="341" alt="testDBT" src="https://github.com/user-attachments/assets/5e604d1e-946a-4a2c-a7a7-0d09e5797364" />


---

## Tabla resumen mensual

dbt genera automáticamente la tabla `monthly_stock_summary` en ClickHouse con los siguientes campos:

| Campo | Descripción |
|---|---|
| ticker | Código del banco |
| month | Mes |
| avg_open_price | Precio promedio de apertura |
| avg_close_price | Precio promedio de cierre |
| avg_price | Promedio entre apertura y cierre |
| avg_volume | Volumen promedio de transacciones |
| trading_days | Días hábiles del mes |

Ejemplo de consulta:
```sql
SELECT * FROM warehouse.monthly_stock_summary
WHERE ticker = 'JPM'
ORDER BY month;
```

---

## Reglas de validación implementadas (dbt)

| Test | Tabla | Campo | Resultado |
|---|---|---|---|
| not_null | stg_daily_prices | ticker | PASS |
| not_null | stg_daily_prices | date | PASS |
| not_null | stg_daily_prices | close | PASS |
| not_null | stg_daily_prices | volume | PASS |

---

## Pipeline orquestado con Airflow

El DAG `mcasb_bank_pipeline` ejecuta 4 tareas en secuencia:

1. `01_extract_from_api` → Extrae datos de Yahoo Finance
2. `02_integrate_to_clickhouse` → Copia datos de PostgreSQL a ClickHouse
3. `03_dbt_transform` → Ejecuta modelos dbt
4. `04_dbt_test` → Valida calidad de los datos

---

## Autor
MCASB - Maridania Cabrera Azcona
