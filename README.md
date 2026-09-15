# Pipeline de extracción de entidades técnicas

Pre-entrega 2: pipeline asíncrono que recibe texto libre y devuelve un objeto Pydantic validado.

## Instalación

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Configurá `OPENAI_API_KEY` en `.env` y ejecutá:

```powershell
python main.py
```

## Qué contiene

- `schemas.py`: modelo Pydantic `EntidadesTecnicas` y enum de criticidad.
- `chain.py`: `ChatPromptTemplate`, `ChatOpenAI`, salida estructurada y reintentos.
- `main.py`: prueba asíncrona con `process_text()` y `.ainvoke()`.

La cadena se construye como `prompt | model.with_structured_output(EntidadesTecnicas) | validador`.
Se usa `include_raw=True` para revisar `finish_reason`; si la respuesta fue truncada, el JSON no se puede parsear o falta un campo obligatorio, se lanza una excepción y `.with_retry()` vuelve a llamar al modelo (hasta 3 intentos en total).

## Salida esperada

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "API con caché en Redis y persistencia en PostgreSQL; hay un problema de conexiones concurrentes."
}
```
