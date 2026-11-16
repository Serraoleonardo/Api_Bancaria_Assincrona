from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Usuario
from app.schemas import Token, UsuarioCreate, UsuarioOut
from app.security import criar_token, gerar_hash_senha, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/cadastro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
async def cadastrar(dados: UsuarioCreate, session: AsyncSession = Depends(get_session)):
    existe = await session.scalar(select(Usuario).where(Usuario.cpf == dados.cpf))
    if existe:
        raise HTTPException(status.HTTP_409_CONFLICT, "CPF já cadastrado")
    usuario = Usuario(nome=dados.nome, cpf=dados.cpf, senha_hash=gerar_hash_senha(dados.senha))
    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """Use o CPF no campo `username`."""
    usuario = await session.scalar(select(Usuario).where(Usuario.cpf == form.username))
    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "CPF ou senha incorretos")
    return Token(access_token=criar_token(usuario.id))
