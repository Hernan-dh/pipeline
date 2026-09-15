"""Contrato de salida del pipeline."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class NivelCriticidad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class EntidadesTecnicas(BaseModel):
    """Información técnica extraída y validada desde un texto libre."""

    model_config = ConfigDict(str_strip_whitespace=True)

    tecnologias: list[str] = Field(
        min_length=1,
        description="Tecnologías, librerías, bases de datos o servicios mencionados.",
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="Impacto técnico estimado: baja, media o alta."
    )
    resumen_tecnico: str = Field(
        min_length=10,
        description="Resumen técnico breve del texto de entrada.",
    )
