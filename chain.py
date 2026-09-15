"""Cadena LCEL para extraer entidades técnicas de texto libre."""

from __future__ import annotations

import logging
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from schemas import EntidadesTecnicas

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

FORMAT_INSTRUCTIONS = (
    "Clasificá la criticidad según el impacto descrito: baja, media o alta. "
    "Completá todos los campos requeridos por el esquema."
)


class RespuestaIncompletaError(ValueError):
    """El modelo no entregó un objeto que cumpla el contrato."""


def validar_salida(response: dict[str, Any]) -> EntidadesTecnicas:
    """Convierte la respuesta estructurada en el modelo o provoca un reintento."""
    raw = response["raw"]
    finish_reason = raw.response_metadata.get("finish_reason")
    if finish_reason in {"length", "max_tokens"}:
        logger.warning("Respuesta truncada (%s); se reintentará.", finish_reason)
        raise RespuestaIncompletaError("La respuesta fue truncada por falta de tokens.")

    if response["parsing_error"] is not None or response["parsed"] is None:
        logger.warning("Salida no parseable; se reintentará.")
        raise RespuestaIncompletaError("El modelo devolvió una salida incompleta o mal formada.")

    try:
        result = EntidadesTecnicas.model_validate(response["parsed"])
    except ValidationError as error:
        logger.warning("Salida inválida para Pydantic; se reintentará.")
        raise RespuestaIncompletaError("La salida no cumple el esquema Pydantic.") from error

    logger.info("Salida validada: %s", result.model_dump())
    return result


def crear_cadena():
    """Construye la cadena sólo al usarla, así importar el módulo no exige una API key."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Falta OPENAI_API_KEY. Copiá .env.example a .env y configurala.")

    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
    structured_model = model.with_structured_output(EntidadesTecnicas, include_raw=True)

    # Esta composición es LCEL: Prompt + LLM con salida estructurada + validación.
    chain = prompt | structured_model | RunnableLambda(validar_salida)
    return chain.with_retry(
        retry_if_exception_type=(RespuestaIncompletaError,),
        stop_after_attempt=3,
    )


async def process_text(text: str) -> EntidadesTecnicas:
    """Procesa texto asíncronamente y devuelve únicamente un objeto validado."""
    logger.info("Iniciando extracción técnica")
    result = await crear_cadena().ainvoke(
        {"text": text, "format_instructions": FORMAT_INSTRUCTIONS}
    )
    logger.info("Extracción finalizada correctamente")
    return result


# El template es modular: LangChain recibe las variables text y format_instructions.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Extraé entidades técnicas del texto. Respondé solamente con los campos "
            "del esquema solicitado. Si no hay una tecnología explícita, usá 'No especificada'.",
        ),
        ("human", "Texto a analizar:\n{text}\n\n{format_instructions}"),
    ]
)
