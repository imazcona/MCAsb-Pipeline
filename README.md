# MCASB Data Pipeline
### Pipeline de datos bancarios - Bolsa de valores USA

Pipeline end-to-end que extrae, integra, valida y transforma datos financieros de bancos que cotizan en la bolsa de Estados Unidos, utilizando datos de Yahoo Finance.

## Arquitectura

![Arquitectura del Pipeline](07_docs/architecture.png)

## Tecnologías utilizadas

| Herramienta | Función | Puerto |
|---|---|---|
| Python + yfinance | Extracción de datos del API | - |
| PostgreSQL 15 | Landing zone (datos crudos) | 5432 |
| ClickHouse 23.8 | Warehouse OLAP (datos curados) | 8123 |
| dbt | Validación y transformación | - |
| Apache Airflow 2.7 | Orquestación del pipeline | 8080 |
| Docker Compose | Contenedorización de servicios | - |

## Datos extraídos (2024-2025)

Se procesan 20 bancos: JPM, BAC, WFC, C, GS, MS, USB, PNC, TFC, COF, BK, STT, FITB, HBAN, MTB, KEY, RF, CFG, ZION, ALLY.

Para cada banco se extraen 5 conjuntos de datos:

1. **Información básica**: industria, sector, empleados, ubicación, website
2. **Precios diarios**: open, high, low, close, volume
3. **Fundamentales**: assets, debt, invested capital, shares issued
4. **Tenedores institucionales**: holder, shares, value
5. **Calificaciones**: upgrades, downgrades de analistas

## Estructura del proyecto
mcasb-pipeline/
├── 01_extraction/        # Script Python (yfinance)
│   └── src/
│       ├── main.py       # Script principal
│       ├── tickers.py    # Lista de 20 bancos
│       └── extractors.py # Funciones de extracción
├── 02_landing_zone/      # SQL de PostgreSQL
│   └── init.sql
├── 03_warehouse/         # SQL de ClickHouse
│   └── init.sql
├── 04_integration/       # Integración PG → ClickHouse
│   └── pg_to_clickhouse.py
├── 05_transformation/    # Modelos dbt
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       └── marts/
├── 06_orchestration/     # DAGs de Airflow
│   └── dags/
│       └── mcasb_pipeline_dag.py
├── 07_docs/              # Documentación
├── docker-compose.yml    # Levanta toda la infra
└── .env                  # Variables de entorno
## Cómo ejecutar el proyecto

### Prerequisitos
- Docker Desktop instalado
- Git instalado

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/imazcona/MCAsb-Pipeline.git
cd MCAsb-Pipeline
```

### Paso 2: Crear archivo .env
```bash
cp .env.example .env
```

### Paso 3: Levantar los servicios
```bash
docker compose up -d
```

### Paso 4: Verificar que los contenedores están corriendo
```bash
docker compose ps
```

### Paso 5: Ejecutar la extracción
```bash
pip install yfinance pandas sqlalchemy psycopg2-binary clickhouse-driver dbt-clickhouse
python 01_extraction/src/main.py
```

### Paso 6: Integrar datos a ClickHouse
```bash
python 04_integration/pg_to_clickhouse.py
```

### Paso 7: Ejecutar transformaciones dbt
```bash
cd 05_transformation
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### Paso 8: Acceder a Airflow
- URL: http://localhost:8080
- Usuario: admin
- Contraseña: admin

## Tabla resumen mensual

dbt genera la tabla `monthly_stock_summary` con:
- Precio promedio de apertura y cierre
- Volumen promedio
- Días de trading por mes

Ejemplo de consulta:
```sql
SELECT * FROM warehouse.monthly_stock_summary
WHERE ticker = 'JPM'
ORDER BY month;
```

## Reglas de validación (dbt tests)
- ticker: NOT NULL en todas las tablas
- date: NOT NULL en precios diarios
- close: NOT NULL (no hay precios vacíos)
- volume: NOT NULL (no hay volúmenes vacíos)

## Autor
MCASB - Subdirección de Gobierno de Datos