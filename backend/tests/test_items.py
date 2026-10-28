"""Tests du CRUD /api/items (base SQLite en mémoire, voir conftest.py)."""


def creer(client, nom="exemple"):
    reponse = client.post("/api/items", json={"name": nom})
    assert reponse.status_code == 201
    return reponse.json()


def test_creer_puis_lire(client):
    cree = creer(client, "premier")

    # L'id et la date sont fabriqués par la base, pas par le client.
    assert cree["name"] == "premier"
    assert isinstance(cree["id"], int)
    assert "created_at" in cree

    lu = client.get(f"/api/items/{cree['id']}")
    assert lu.status_code == 200
    assert lu.json() == cree


def test_lister_avec_pagination(client):
    for n in range(3):
        creer(client, f"item {n}")

    assert len(client.get("/api/items").json()) == 3
    assert len(client.get("/api/items?limit=2").json()) == 2
    # offset=2 : on saute les 2 premiers, il en reste 1.
    assert len(client.get("/api/items?limit=2&offset=2").json()) == 1


def test_modifier(client):
    cree = creer(client, "avant")

    reponse = client.put(f"/api/items/{cree['id']}", json={"name": "apres"})

    assert reponse.status_code == 200
    assert reponse.json()["name"] == "apres"
    assert client.get(f"/api/items/{cree['id']}").json()["name"] == "apres"


def test_supprimer(client):
    cree = creer(client)

    reponse = client.delete(f"/api/items/{cree['id']}")

    assert reponse.status_code == 204
    assert reponse.content == b""
    assert client.get(f"/api/items/{cree['id']}").status_code == 404


def test_element_introuvable(client):
    assert client.get("/api/items/999").status_code == 404
    assert client.put("/api/items/999", json={"name": "x"}).status_code == 404
    assert client.delete("/api/items/999").status_code == 404


def test_nom_nettoye(client):
    # Les espaces en début et fin de nom sont retirés.
    assert creer(client, "  espace  ")["name"] == "espace"


def test_nom_invalide_refuse(client):
    # 422 = la requête est refusée avant même d'atteindre la base.
    assert client.post("/api/items", json={"name": ""}).status_code == 422
    assert client.post("/api/items", json={"name": "   "}).status_code == 422
    assert client.post("/api/items", json={"name": "x" * 101}).status_code == 422
    assert client.post("/api/items", json={}).status_code == 422


def test_parametres_hors_bornes_refuses(client):
    assert client.get("/api/items?limit=0").status_code == 422
    assert client.get("/api/items?limit=101").status_code == 422
    assert client.get("/api/items?offset=-1").status_code == 422
    assert client.get("/api/items/abc").status_code == 422
