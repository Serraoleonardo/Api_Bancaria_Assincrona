import pytest

pytestmark = pytest.mark.asyncio


async def abrir_conta(client, headers) -> int:
    r = await client.post("/contas", headers=headers)
    assert r.status_code == 201
    return r.json()["id"]


async def test_login_invalido(client):
    r = await client.post("/auth/login", data={"username": "000", "password": "x"})
    assert r.status_code == 401


async def test_rota_protegida_sem_token(client):
    r = await client.get("/contas")
    assert r.status_code == 401


async def test_deposito_saque_e_extrato(client, auth_headers):
    conta_id = await abrir_conta(client, auth_headers)

    r = await client.post(f"/contas/{conta_id}/transacoes", headers=auth_headers,
                          json={"tipo": "deposito", "valor": "150.50"})
    assert r.status_code == 201
    assert r.json()["saldo_apos"] == "150.50"

    r = await client.post(f"/contas/{conta_id}/transacoes", headers=auth_headers,
                          json={"tipo": "saque", "valor": "50.25"})
    assert r.status_code == 201
    assert r.json()["saldo_apos"] == "100.25"

    r = await client.get(f"/contas/{conta_id}/extrato", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["conta"]["saldo"] == "100.25"
    assert [t["tipo"] for t in body["transacoes"]] == ["deposito", "saque"]


async def test_saque_sem_saldo(client, auth_headers):
    conta_id = await abrir_conta(client, auth_headers)
    r = await client.post(f"/contas/{conta_id}/transacoes", headers=auth_headers,
                          json={"tipo": "saque", "valor": "10"})
    assert r.status_code == 400


@pytest.mark.parametrize("valor", ["0", "-5"])
async def test_valor_invalido(client, auth_headers, valor):
    conta_id = await abrir_conta(client, auth_headers)
    r = await client.post(f"/contas/{conta_id}/transacoes", headers=auth_headers,
                          json={"tipo": "deposito", "valor": valor})
    assert r.status_code == 422


async def test_cpf_duplicado(client, auth_headers):
    r = await client.post("/auth/cadastro", json={"nome": "Outro", "cpf": "12345678900", "senha": "abcdef"})
    assert r.status_code == 409


async def test_token_invalido(client):
    r = await client.get("/contas", headers={"Authorization": "Bearer token-falso"})
    assert r.status_code == 401


async def test_usuario_nao_acessa_conta_de_outro(client, auth_headers):
    conta_id = await abrir_conta(client, auth_headers)

    await client.post("/auth/cadastro", json={"nome": "Maria", "cpf": "98765432100", "senha": "outra123"})
    r = await client.post("/auth/login", data={"username": "98765432100", "password": "outra123"})
    headers_maria = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r = await client.get(f"/contas/{conta_id}/extrato", headers=headers_maria)
    assert r.status_code == 404
    r = await client.post(f"/contas/{conta_id}/transacoes", headers=headers_maria,
                          json={"tipo": "deposito", "valor": "10"})
    assert r.status_code == 404


async def test_saque_do_saldo_exato(client, auth_headers):
    conta_id = await abrir_conta(client, auth_headers)
    await client.post(f"/contas/{conta_id}/transacoes", headers=auth_headers,
                      json={"tipo": "deposito", "valor": "80"})
    r = await client.post(f"/contas/{conta_id}/transacoes", headers=auth_headers,
                          json={"tipo": "saque", "valor": "80"})
    assert r.status_code == 201
    assert r.json()["saldo_apos"] == "0.00"


@pytest.mark.parametrize("cpf", ["123", "1234567890123", "abc"])
async def test_cadastro_cpf_invalido(client, cpf):
    r = await client.post("/auth/cadastro", json={"nome": "Teste", "cpf": cpf, "senha": "segredo123"})
    assert r.status_code == 422
