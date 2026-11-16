import pytest

pytestmark = pytest.mark.asyncio


async def preparar_conta(client, headers) -> int:
    conta_id = (await client.post("/contas", headers=headers)).json()["id"]
    for tipo, valor in [("deposito", "100"), ("deposito", "50"), ("saque", "30"), ("deposito", "10")]:
        await client.post(f"/contas/{conta_id}/transacoes", headers=headers, json={"tipo": tipo, "valor": valor})
    return conta_id


async def test_extrato_filtra_por_tipo(client, auth_headers):
    conta_id = await preparar_conta(client, auth_headers)
    r = await client.get(f"/contas/{conta_id}/extrato?tipo=saque", headers=auth_headers)
    assert r.status_code == 200
    transacoes = r.json()["transacoes"]
    assert len(transacoes) == 1
    assert transacoes[0]["valor"] == "30.00"


async def test_extrato_paginado(client, auth_headers):
    conta_id = await preparar_conta(client, auth_headers)
    r = await client.get(f"/contas/{conta_id}/extrato?limit=2&offset=1", headers=auth_headers)
    valores = [t["valor"] for t in r.json()["transacoes"]]
    assert valores == ["50.00", "30.00"]


async def test_extrato_limit_invalido(client, auth_headers):
    conta_id = await preparar_conta(client, auth_headers)
    r = await client.get(f"/contas/{conta_id}/extrato?limit=0", headers=auth_headers)
    assert r.status_code == 422
