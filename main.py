"""Mini-script asíncrono de prueba."""

import asyncio

from chain import process_text


TEXT_EXAMPLE = """
Una API creada con FastAPI usa Redis para caché y PostgreSQL para persistencia.
Durante picos de tráfico se agotan las conexiones concurrentes a la base de datos.
"""


async def main() -> None:
    result = await process_text(TEXT_EXAMPLE)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
