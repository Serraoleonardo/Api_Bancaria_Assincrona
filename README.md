# 🏦 API Bancária Assíncrona

[![Testes](https://github.com/Serraoleonardo/Api_Bancaria_Assincrona/actions/workflows/tests.yml/badge.svg)](https://github.com/Serraoleonardo/Api_Bancaria_Assincrona/actions/workflows/tests.yml)

API RESTful **assíncrona** para operações bancárias — depósitos, saques e extrato — com autenticação **JWT**. Projeto desenvolvido para o desafio de curso da [DIO](https://www.dio.me/).

## ✨ Funcionalidades

- **Cadastro e login** de usuários (CPF + senha), com senha armazenada em hash (PBKDF2-SHA256)
- **Autenticação JWT** protegendo todas as rotas de conta
- **Abertura de contas** correntes vinculadas ao usuário
- **Transações** de depósito e saque
- **Extrato** com saldo após cada transação, filtro por tipo e paginação
- **Regras de negócio**
  - Não aceita valores zerados ou negativos
  - Não permite saque sem saldo suficiente
  - Usuário só acessa as próprias contas
  - CPF único por usuário

## 🛠️ Tecnologias

| Camada | Ferramenta |
|---|---|
| Framework web | FastAPI (async) |
| Banco de dados | SQLite com SQLAlchemy 2.0 assíncrono + aiosqlite |
| Validação | Pydantic v2 |
| Autenticação | JWT (PyJWT) + OAuth2 Password Flow |
| Testes | Pytest + pytest-asyncio + HTTPX |
| CI | GitHub Actions |
| Container | Docker |

## 📁 Estrutura

```
app/
├── main.py          # Criação da app e registro das rotas
├── config.py        # Configurações via variáveis de ambiente
├── database.py      # Engine e sessão assíncronas
├── models.py        # Tabelas: Usuario, Conta, Transacao
├── schemas.py       # Modelos de entrada/saída (Pydantic)
├── security.py      # Hash de senha, JWT e usuário autenticado
└── routers/
    ├── auth.py      # /auth/cadastro e /auth/login
    └── contas.py    # Contas, transações e extrato
tests/
└── test_api.py      # Testes de ponta a ponta
```

## 🚀 Como rodar

```bash
git clone https://github.com/Serraoleonardo/Api_Bancaria_Assincrona.git
cd Api_Bancaria_Assincrona
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # ajuste a SECRET_KEY
uvicorn app.main:app --reload
```

Acesse a documentação interativa em **http://localhost:8000/docs**.

### Com Docker

```bash
docker build -t api-bancaria .
docker run -p 8000:8000 api-bancaria
```

## 📌 Endpoints

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| POST | `/auth/cadastro` | Cadastra um usuário | — |
| POST | `/auth/login` | Retorna o token JWT (CPF no campo `username`) | — |
| POST | `/contas` | Abre uma nova conta | ✅ |
| GET | `/contas` | Lista as contas do usuário | ✅ |
| POST | `/contas/{id}/transacoes` | Registra depósito ou saque | ✅ |
| GET | `/contas/{id}/extrato` | Exibe saldo e histórico (`?tipo=`, `?limit=`, `?offset=`) | ✅ |

### Exemplo de transação

```json
POST /contas/1/transacoes
{
  "tipo": "deposito",
  "valor": "150.50"
}
```

## ✅ Testes

```bash
pytest
```

Os testes rodam automaticamente a cada push via GitHub Actions e cobrem:

- Login inválido, rota sem token e token falso
- Depósito, saque e extrato (inclusive saque do saldo exato)
- Saque sem saldo e valores zerados/negativos
- CPF duplicado ou inválido
- Isolamento: um usuário não acessa a conta de outro
- Filtro e paginação do extrato

## 👤 Autor

**Leonardo Serrão** — [GitHub](https://github.com/Serraoleonardo)
