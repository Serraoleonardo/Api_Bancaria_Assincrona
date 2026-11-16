from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import TipoTransacao


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    cpf: str = Field(description="Apenas números (11 dígitos)")
    senha: str = Field(min_length=6)

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        digitos = "".join(c for c in v if c.isdigit())
        if len(digitos) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return digitos


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    cpf: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ContaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    agencia: str
    numero: str
    saldo: Decimal
    criada_em: datetime


class TransacaoIn(BaseModel):
    tipo: TipoTransacao
    valor: Decimal = Field(gt=0, max_digits=14, decimal_places=2, description="Valor positivo")


class TransacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: TipoTransacao
    valor: Decimal
    saldo_apos: Decimal
    realizada_em: datetime


class Extrato(BaseModel):
    conta: ContaOut
    transacoes: list[TransacaoOut]
