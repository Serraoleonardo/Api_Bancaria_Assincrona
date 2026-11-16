import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class TipoTransacao(str, enum.Enum):
    deposito = "deposito"
    saque = "saque"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    cpf: Mapped[str] = mapped_column(String(11), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    contas: Mapped[list["Conta"]] = relationship(back_populates="titular")


class Conta(Base):
    __tablename__ = "contas"

    id: Mapped[int] = mapped_column(primary_key=True)
    agencia: Mapped[str] = mapped_column(String(4), default="0001")
    numero: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    titular: Mapped[Usuario] = relationship(back_populates="contas")
    transacoes: Mapped[list["Transacao"]] = relationship(
        back_populates="conta", order_by="Transacao.realizada_em"
    )


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    conta_id: Mapped[int] = mapped_column(ForeignKey("contas.id"), index=True)
    tipo: Mapped[TipoTransacao] = mapped_column(Enum(TipoTransacao))
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    saldo_apos: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    realizada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    conta: Mapped[Conta] = relationship(back_populates="transacoes")
