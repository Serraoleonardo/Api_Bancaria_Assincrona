import secrets
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Conta, TipoTransacao, Transacao, Usuario
from app.schemas import ContaOut, Extrato, TransacaoIn, TransacaoOut
from app.security import usuario_atual

router = APIRouter(prefix="/contas", tags=["Contas e transações"])


async def _conta_do_usuario(conta_id: int, usuario: Usuario, session: AsyncSession) -> Conta:
    conta = await session.get(Conta, conta_id)
    if conta is None or conta.usuario_id != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conta não encontrada")
    return conta


@router.post("", response_model=ContaOut, status_code=status.HTTP_201_CREATED)
async def abrir_conta(
    usuario: Usuario = Depends(usuario_atual),
    session: AsyncSession = Depends(get_session),
):
    conta = Conta(numero=f"{secrets.randbelow(10**8):08d}", usuario_id=usuario.id, saldo=Decimal("0.00"))
    session.add(conta)
    await session.commit()
    await session.refresh(conta)
    return conta


@router.get("", response_model=list[ContaOut])
async def listar_contas(
    usuario: Usuario = Depends(usuario_atual),
    session: AsyncSession = Depends(get_session),
):
    result = await session.scalars(select(Conta).where(Conta.usuario_id == usuario.id))
    return result.all()


@router.post("/{conta_id}/transacoes", response_model=TransacaoOut, status_code=status.HTTP_201_CREATED)
async def registrar_transacao(
    conta_id: int,
    dados: TransacaoIn,
    usuario: Usuario = Depends(usuario_atual),
    session: AsyncSession = Depends(get_session),
):
    conta = await _conta_do_usuario(conta_id, usuario, session)

    if dados.tipo == TipoTransacao.saque:
        if dados.valor > conta.saldo:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Saldo insuficiente para o saque")
        conta.saldo -= dados.valor
    else:
        conta.saldo += dados.valor

    transacao = Transacao(conta_id=conta.id, tipo=dados.tipo, valor=dados.valor, saldo_apos=conta.saldo)
    session.add(transacao)
    await session.commit()
    await session.refresh(transacao)
    return transacao


@router.get("/{conta_id}/extrato", response_model=Extrato)
async def extrato(
    conta_id: int,
    tipo: TipoTransacao | None = Query(None, description="Filtra por depósito ou saque"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    usuario: Usuario = Depends(usuario_atual),
    session: AsyncSession = Depends(get_session),
):
    conta = await _conta_do_usuario(conta_id, usuario, session)
    consulta = select(Transacao).where(Transacao.conta_id == conta.id)
    if tipo is not None:
        consulta = consulta.where(Transacao.tipo == tipo)
    consulta = consulta.order_by(Transacao.realizada_em, Transacao.id).limit(limit).offset(offset)
    result = await session.scalars(consulta)
    return Extrato(conta=ContaOut.model_validate(conta), transacoes=result.all())
