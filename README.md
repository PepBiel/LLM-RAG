# AgroOps Copilot API

API en FastAPI para un copiloto de operaciones agricolas. El proyecto combina RAG sobre documentos tecnicos del dominio agricola con datos operativos simulados de parcelas, sensores, incidencias y alertas.

La idea no es hacer un simple "chat con PDFs", sino construir un backend de IA aplicada: los documentos se cargan, se dividen en chunks, se convierten en embeddings, se guardan en una base vectorial persistente, se recuperan por similitud, se inyectan en un prompt y se envian a un LLM para generar una respuesta trazable con fuentes.

## Objetivo Del Proyecto

Este MVP demuestra que sabes disenar una solucion de IA aplicada a producto, no solo llamar a un modelo.

El sistema permite preguntas como:

```text
La parcela de tomate tiene humedad baja y hojas amarillas. Que revisarias primero?
```

Y responde usando:

- Documentos tecnicos recuperados mediante RAG.
- Datos estructurados simulados de una parcela realista.
- Un LLM desacoplado mediante adapters.
- Fuentes usadas en la respuesta.
- Metadatos como latencia, modelo, chunks recuperados y coleccion vectorial.

## Idea Central

RAG significa Retrieval-Augmented Generation. En espanol: generacion aumentada con recuperacion.

Un LLM por si solo responde usando lo que aprendio durante entrenamiento y el contexto que le pasas. El problema es que puede inventar, no conoce tus documentos privados y no sabe el estado actual de tus parcelas. RAG soluciona parte de esto:

```text
1. Guardas documentos relevantes en una base vectorial.
2. Cuando llega una pregunta, buscas los fragmentos mas parecidos.
3. Construyes un prompt con esos fragmentos y la pregunta.
4. Envias ese prompt al LLM.
5. Devuelves respuesta + fuentes + metadatos.
```

En este proyecto, ademas de documentos, tambien se inyectan datos operativos simulados:

```text
sensores + incidencias + alertas + parcelas + documentos recuperados -> prompt -> LLM
```

## Arquitectura General

```text
Cliente / Swagger / curl
        |
        v
FastAPI
        |
        +-- /health
        +-- /ask
        +-- /diagnose
        +-- /documents
        +-- /operations
        |
        v
Servicios de aplicacion
        |
        +-- RagService
        |      +-- embeddings
        |      +-- vector store
        |      +-- prompt
        |      +-- LLM provider
        |
        +-- IngestionService
        |      +-- carga documento
        |      +-- chunking
        |      +-- embeddings
        |      +-- upsert en Chroma
        |
        +-- OperationsService
        |      +-- parcelas
        |      +-- sensores
        |      +-- incidencias
        |      +-- alertas
        |
        +-- DiagnosisService
               +-- combina RAG + datos operativos
```

## Estructura Del Repositorio

```text
app/
|-- main.py                         # Crea la app FastAPI y registra routers
|-- api/
|   |-- dependencies.py             # Inyeccion de dependencias
|   |-- routes_ask.py               # Endpoints /ask y /diagnose
|   |-- routes_documents.py         # Endpoints de documentos
|   |-- routes_health.py            # Endpoint /health
|   |-- routes_operations.py        # Endpoints de datos operativos
|
|-- core/
|   |-- config.py                   # Settings desde variables de entorno y .env
|   |-- timing.py                   # Medicion simple de latencia
|
|-- schemas/
|   |-- ask.py                      # Request/response de RAG y diagnostico
|   |-- documents.py                # Schemas de ingestion y listado
|   |-- operations.py               # Schemas de parcelas, sensores, alertas
|   |-- health.py                   # Schema de healthcheck
|
|-- services/
|   |-- chunking.py                 # Normalizacion y division en chunks
|   |-- document_loader.py          # Lectura de .md, .txt y .pdf
|   |-- ingestion_service.py        # Pipeline de ingestion
|   |-- rag_service.py              # Retrieval + prompt + LLM
|   |-- diagnosis_service.py        # Combina parcela + RAG
|   |-- operations_service.py       # Carga datos demo
|
|-- embeddings/
|   |-- base.py                     # Interfaz comun
|   |-- factory.py                  # Seleccion de provider
|   |-- hash_provider.py            # Embeddings offline deterministas
|   |-- sentence_transformers_provider.py
|
|-- vectorstore/
|   |-- base.py                     # Interfaz comun
|   |-- chroma_store.py             # Adapter de ChromaDB
|
|-- llm/
|   |-- base.py                     # Interfaz comun para LLMs
|   |-- factory.py                  # Seleccion de provider
|   |-- mock.py                     # LLM falso para desarrollo local
|   |-- openai_compatible.py        # OpenRouter, OpenAI y Groq
|
|-- data/
    |-- demo_operations.json        # Datos simulados de parcelas y sensores
    |-- corpus_manifest.yml         # Manifest del corpus demo

data/
|-- raw/                            # Documentos demo en Markdown
|-- processed/                      # Reservado para artefactos procesados
|-- chroma/                         # Base vectorial persistente, ignorada por git

scripts/
|-- build_index.py                  # Construye el indice vectorial
|-- ingest_document.py              # Ingresa un documento local
|-- seed_demo_data.py               # Comprueba datos operativos demo

tests/
|-- test_api.py
|-- test_chunking.py
|-- test_embeddings.py
|-- test_operations_service.py
```

## Stack Tecnico

- Python 3.11+
- FastAPI
- Pydantic v2
- ChromaDB como base vectorial persistente
- OpenRouter, OpenAI y Groq mediante adapter compatible con OpenAI
- Provider `mock` para ejecutar sin API key
- Embeddings `hash` offline por defecto
- Opcion de `sentence-transformers` para embeddings semanticos reales
- pytest para tests
- Docker y docker-compose

Decision importante: no se usa LangChain en el MVP. Esto hace que el flujo sea mas explicable:

```text
documentos -> chunks -> embeddings -> Chroma -> retrieval -> prompt -> LLM -> respuesta
```

## Como Ejecutarlo Desde Cero

En Windows PowerShell:

```powershell
cd "C:\Users\Pep Biel\Documents\GitHub\LLM-RAG"
```

Crear entorno virtual:

```powershell
py -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
python -m pip install -e ".[dev]"
```

Crear el indice vectorial:

```powershell
python scripts\build_index.py --reset
```

Arrancar la API:

```powershell
python -m uvicorn app.main:app --reload
```

Abrir Swagger:

```text
http://127.0.0.1:8000/docs
```

## Endpoints Del MVP

```text
GET  /health
POST /ask
POST /diagnose
POST /documents/ingest
GET  /documents
GET  /operations/plots
GET  /operations/plots/{plot_id}/status
```

## Como Funciona FastAPI En Este Proyecto

El punto de entrada es `app/main.py`.

Ese archivo crea la aplicacion:

```python
app = FastAPI(...)
```

Y registra routers:

```python
app.include_router(routes_health.router)
app.include_router(routes_ask.router)
app.include_router(routes_documents.router)
app.include_router(routes_operations.router)
```

Cada router agrupa endpoints de una parte del producto:

- `routes_health.py`: comprueba que la API responde y cuantos chunks hay indexados.
- `routes_ask.py`: contiene `/ask` y `/diagnose`.
- `routes_documents.py`: permite listar documentos e ingestar documentos nuevos.
- `routes_operations.py`: expone parcelas y estado operativo simulado.

FastAPI usa los schemas de Pydantic para validar entradas y salidas. Por ejemplo, `/ask` recibe un `AskRequest` y devuelve un `AskResponse`.

Esto te da tres ventajas:

- Validacion automatica.
- Documentacion automatica en Swagger.
- Contrato claro entre frontend/cliente y backend.

## Inyeccion De Dependencias

El archivo `app/api/dependencies.py` crea los objetos principales:

- Provider de embeddings.
- Vector store.
- Provider de LLM.
- Servicios de RAG, ingestion, operaciones y diagnostico.

FastAPI los inyecta en los endpoints con `Depends`.

Ejemplo conceptual:

```text
POST /ask
  |
  v
FastAPI crea o reutiliza RagService
  |
  v
RagService ejecuta retrieval + LLM
```

Esto evita crear manualmente servicios dentro de cada endpoint y hace mas facil testear.

## Corpus Demo: De Donde Salen Los Documentos

Los documentos demo estan en:

```text
data/raw/
```

Son notas tecnicas creadas para este proyecto, con temas como:

- Programacion de riego.
- Uso operativo de sensores de humedad.
- Principios de IPM.
- Diagnostico inicial de hojas amarillas en tomate.
- Checklist de riego por goteo.
- Riesgo de estres por calor.

El archivo `app/data/corpus_manifest.yml` define que documentos forman parte del corpus.

Cada entrada incluye:

```yaml
document_id: drip_irrigation_troubleshooting
title: "Drip irrigation troubleshooting checklist"
local_path: "data/raw/drip_irrigation_troubleshooting.md"
source_url: "..."
publisher: "Demo corpus"
topic: "irrigation"
crops: ["tomato", "vegetables"]
license_note: "..."
```

El manifest es importante porque no solo apunta al texto, tambien guarda metadatos utiles para trazabilidad.

## Pipeline De Ingestion

La ingestion es el proceso de meter documentos en la base vectorial.

Se ejecuta con:

```powershell
python scripts\build_index.py --reset
```

Ese script hace lo siguiente:

```text
1. Lee app/data/corpus_manifest.yml.
2. Crea el provider de embeddings.
3. Crea la conexion a ChromaDB.
4. Si usas --reset, borra y recrea la coleccion.
5. Para cada documento del manifest, llama a IngestionService.
```

El flujo interno de `IngestionService` es:

```text
DocumentIngestRequest
        |
        v
cargar texto desde local_path o request.text
        |
        v
crear document_id
        |
        v
dividir texto en chunks
        |
        v
crear embedding para cada chunk
        |
        v
guardar ids + textos + embeddings + metadatos en Chroma
```

## Que Es Un Chunk

Un chunk es un fragmento pequeno de un documento.

No metemos el documento entero al LLM porque:

- Puede ser demasiado largo.
- Puede superar el limite de tokens.
- Puede meter informacion irrelevante.
- Es mas dificil recuperar partes concretas.

En este proyecto, el chunking esta en:

```text
app/services/chunking.py
```

Primero se normaliza el texto:

```text
"hola\n\n mundo" -> "hola mundo"
```

Luego se divide usando:

```text
CHUNK_SIZE=900
CHUNK_OVERLAP=150
```

Esto significa:

- Cada chunk intenta tener unas 900 caracteres.
- Cada chunk comparte 150 caracteres con el anterior.

El overlap sirve para no perder contexto entre cortes. Si una explicacion empieza al final de un chunk y termina al inicio del siguiente, el overlap ayuda a conservar continuidad.

## Como Se Crean Los Embeddings

Un embedding es un vector numerico que representa el significado aproximado de un texto.

Ejemplo conceptual:

```text
"riego por goteo y humedad baja" -> [0.12, -0.04, 0.88, ...]
```

La base vectorial no compara texto directamente. Compara vectores.

En este proyecto hay dos opciones:

### 1. Hash Embeddings

Es el modo por defecto:

```env
EMBEDDING_PROVIDER=hash
```

Esta implementado en:

```text
app/embeddings/hash_provider.py
```

Ventaja:

- Funciona offline.
- No necesita API key.
- No descarga modelos.
- Es determinista y va bien para tests.

Limitacion:

- No entiende semantica real como un modelo de embeddings entrenado.
- Sirve para MVP y pruebas, pero no es lo ideal en produccion.

### 2. Sentence Transformers

Modo mas realista:

```env
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Ventaja:

- Recuperacion semantica mucho mejor.

Tradeoff:

- Descarga un modelo.
- Consume mas recursos.
- Anade dependencia mas pesada.

## Como Se Crea La Base Vectorial

La base vectorial se crea con ChromaDB en:

```text
app/vectorstore/chroma_store.py
```

La configuracion esta en:

```text
CHROMA_PATH=data/chroma
CHROMA_COLLECTION=agroops_documents
```

Cuando se crea el `ChromaVectorStore`, se ejecuta conceptualmente:

```python
chromadb.PersistentClient(path="data/chroma")
```

Eso significa que la base no vive solo en memoria. Se guarda en disco dentro de `data/chroma`.

Cada chunk se guarda con:

- `id`: identificador unico del chunk.
- `document`: texto del chunk.
- `embedding`: vector numerico.
- `metadata`: titulo, fuente, publisher, crop, topic, indice del chunk, licencia.

Ejemplo de ID:

```text
drip_irrigation_troubleshooting:chunk:0001
```

## Que Pasa Cuando Preguntas En /ask

Endpoint:

```text
POST /ask
```

Ejemplo:

```json
{
  "question": "Como reviso una parcela de tomate con humedad baja?",
  "top_k": 5,
  "include_context": true
}
```

Flujo:

```text
1. FastAPI valida el JSON con AskRequest.
2. El endpoint llama a RagService.answer().
3. La pregunta se convierte en embedding.
4. Chroma busca los top_k chunks mas parecidos.
5. RagService construye un prompt.
6. El prompt se envia al LLM provider.
7. Se devuelve AskResponse con answer, sources, metadata y contexts opcionales.
```

## Retrieval: Como Se Recuperan Los Chunks

El retrieval ocurre aqui:

```text
app/vectorstore/chroma_store.py
```

La busqueda recibe:

```text
query_embedding
top_k
filters opcionales
```

Chroma compara el vector de la pregunta con los vectores guardados en la coleccion.

Devuelve:

- IDs de chunks.
- Texto de chunks.
- Metadatos.
- Distancias.

El proyecto transforma la distancia en un score aproximado:

```python
score = max(0.0, 1.0 - distance)
```

Cuanto mas alto el score, mas parecido se considera el chunk.

## Como Se Conecta El RAG Al LLM

La conexion ocurre en `RagService`.

Primero recupera contexto documental:

```text
results = vector_store.search(...)
```

Luego construye un prompt con esta estructura:

```text
PREGUNTA
...

DATOS OPERATIVOS
...

CONTEXTO DOCUMENTAL
[S1] title=...; source_url=...; score=...
texto del chunk

[S2] title=...; source_url=...; score=...
texto del chunk

INSTRUCCIONES
- Responde con recomendaciones operativas priorizadas.
- Cita los titulos de las fuentes usadas cuando sean relevantes.
- No inventes valores que no esten en datos operativos o documentos.
- Si falta informacion, di que dato revisarias despues.
```

Despues llama al provider:

```python
llm_response = self._llm_provider.generate([...])
```

El LLM no busca documentos por si mismo. El backend ya ha buscado los chunks relevantes y se los pasa dentro del prompt.

Esta es la idea clave:

```text
RAG no sustituye al LLM.
RAG prepara mejor el contexto que recibe el LLM.
```

## Providers De LLM

Los providers estan en:

```text
app/llm/
```

Hay una interfaz comun:

```text
LLMProvider
```

Y varias implementaciones:

- `MockLLMProvider`: respuesta falsa para desarrollo local.
- `OpenAICompatibleProvider`: cliente generico compatible con APIs tipo OpenAI.

OpenRouter, OpenAI y Groq usan el mismo adapter porque sus APIs de chat son compatibles con el formato de OpenAI:

```text
POST /chat/completions
messages = [
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."}
]
```

Seleccionas el provider con:

```env
LLM_PROVIDER=mock
```

O:

```env
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-4o-mini
OPENROUTER_API_KEY=...
```

Ventaja de esta arquitectura:

```text
El RAG no sabe si detras hay OpenRouter, OpenAI, Groq o mock.
Solo llama a llm_provider.generate().
```

Eso permite cambiar de proveedor sin tocar endpoints ni servicios.

## Que Pasa En /diagnose

Endpoint:

```text
POST /diagnose
```

Ejemplo:

```json
{
  "plot_id": "plot-north-tomato-01",
  "question": "La parcela tiene humedad baja y hojas amarillas. Que revisarias primero?",
  "top_k": 5
}
```

Este endpoint es mas interesante que `/ask`, porque mezcla RAG con datos estructurados.

Flujo:

```text
1. FastAPI valida DiagnoseRequest.
2. DiagnosisService busca el estado de la parcela.
3. OperationsService carga sensores, alertas e incidencias.
4. Se crea un contexto operativo en texto.
5. Se genera una query de busqueda enriquecida.
6. RagService recupera documentos relevantes.
7. RagService construye prompt con datos operativos + documentos.
8. El LLM genera una recomendacion.
9. La API devuelve respuesta, fuentes y metadatos.
```

Ejemplo de contexto operativo:

```text
Parcela: North Tomato Block
Cultivo: tomato
Suelo: sandy loam
Riego: drip
Ultimo sensor: humedad_suelo=13.8%
Alertas abiertas:
- high: low_soil_moisture
Incidencias:
- medium: yellowing_leaves
```

Esto demuestra mentalidad de producto: el sistema no responde solo con documentos, tambien usa el estado operativo de la finca.

## Forma De La Respuesta

La respuesta principal sigue este contrato:

```json
{
  "answer": "...",
  "sources": [
    {
      "document_id": "drip_irrigation_troubleshooting",
      "chunk_id": "drip_irrigation_troubleshooting:chunk:0001",
      "title": "Drip irrigation troubleshooting checklist",
      "source_url": "...",
      "score": 0.82,
      "metadata": {
        "publisher": "Demo corpus",
        "topic": "irrigation",
        "crops": ["tomato", "vegetables"],
        "chunk_index": 1,
        "license_note": "..."
      }
    }
  ],
  "metadata": {
    "latency_ms": 120,
    "llm_provider": "mock",
    "llm_model": "mock-agronomy-advisor",
    "embedding_model": "hashing-384",
    "collection": "agroops_documents",
    "top_k": 5,
    "retrieved_chunks": 5,
    "used_operational_context": true
  },
  "contexts": null
}
```

Esto es importante para portfolio porque no devuelves solo texto. Devuelves trazabilidad.

## Datos Operativos Simulados

Los datos estan en:

```text
app/data/demo_operations.json
```

Incluyen:

- Parcelas.
- Cultivos.
- Tipo de suelo.
- Sistema de riego.
- Sensores.
- Alertas.
- Incidencias.

Ejemplo de parcela:

```text
plot-north-tomato-01
crop: tomato
soil_type: sandy loam
irrigation_system: drip
```

Este diseno permite evolucionar facilmente:

```text
JSON demo -> SQLite -> Postgres -> datos IoT reales
```

## Comandos Utiles

Crear o reconstruir indice:

```powershell
python scripts\build_index.py --reset
```

Listar documentos indexados desde API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/documents
```

Ver healthcheck:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Probar `/diagnose`:

```powershell
$body = @{
  plot_id = "plot-north-tomato-01"
  question = "La parcela tiene humedad baja y hojas amarillas. Que revisarias primero?"
  top_k = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/diagnose `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

Ejecutar tests:

```powershell
python -m pytest
```

Ejecutar lint:

```powershell
python -m ruff check app scripts tests
```

## Docker

Crear `.env`:

```powershell
copy .env.example .env
```

Levantar con Docker:

```powershell
docker compose up --build
```

El `docker-compose.yml` construye el indice al arrancar y expone la API en:

```text
http://127.0.0.1:8000
```

## Configuracion De LLM

Modo local por defecto:

```env
LLM_PROVIDER=mock
LLM_MODEL=mock-agronomy-advisor
```

Este modo no llama a ningun modelo real. Sirve para probar el pipeline completo sin coste.

OpenRouter:

```env
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-4o-mini
OPENROUTER_API_KEY=tu_api_key
```

OpenAI:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=tu_api_key
```

Groq:

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=tu_api_key
```

## Limitaciones Actuales

- El provider de embeddings por defecto (`hash`) no es semantico real.
- El corpus demo es pequeno.
- Los datos operativos son simulados.
- No hay autenticacion.
- No hay evaluacion automatica de calidad RAG.
- No hay base relacional todavia.
- El sistema no debe presentarse como diagnostico agronomico certificado.

Estas limitaciones son aceptables para un MVP portfolio si las explicas bien.

## Roadmap Razonable

Siguientes mejoras defendibles:

- Cambiar embeddings hash por `sentence-transformers`.
- Anadir evaluacion RAG con preguntas esperadas.
- Guardar operaciones en SQLite o Postgres.
- Anadir filtros por cultivo, topic o publisher.
- Integrar clima real con NASA POWER.
- Anadir autenticacion basica.
- Anadir Qdrant como vector store externo.
- Crear un frontend simple para operadores.

## Como Explicarlo En Entrevista

Una buena explicacion corta:

```text
Construí una API en FastAPI para un copiloto agricola. El sistema ingesta documentos tecnicos, los divide en chunks, genera embeddings y los guarda en ChromaDB. Cuando llega una pregunta, convierte la pregunta en embedding, recupera los chunks mas relevantes, combina ese contexto con datos operativos simulados de sensores e incidencias, construye un prompt y lo envia a un LLM mediante un adapter desacoplado. La respuesta devuelve texto, fuentes, scores y metadatos de ejecucion.
```

Puntos fuertes:

- Entiendes el flujo RAG completo.
- No dependes de LangChain para explicar la arquitectura.
- Separas API, servicios, embeddings, vector store y LLM.
- Has modelado datos de dominio.
- Devuelves trazabilidad y no solo una respuesta generada.
- El proyecto puede evolucionar de MVP a producto real.

## Referencias Publicas Del Dominio

- USDA copyright y dominio publico: https://www.usda.gov/about-usda/policies-and-links
- USDA NRCS Irrigation Guide: https://directives.nrcs.usda.gov/sites/default/files2/1712930990/7385.pdf
- USDA Integrated Pest Management: https://www.usda.gov/oce/pest/integrated-pest-management
- NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- USDA QuickStats API: https://quickstats.nass.usda.gov/api
- Cropland Data Layer: https://catalog.data.gov/dataset/cropscape-cropland-data-layer

