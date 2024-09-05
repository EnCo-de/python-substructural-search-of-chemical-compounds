from time import sleep
from pytest import mark, fixture
from starlette.testclient import TestClient
from src.main import app, redis_client
# (substructure_search, get_server, retrieve_all_molecules, 
#                    add_molecule_smiles, retrieve_molecule_by_id, update_molecule, 
#                    delete_molecule, search_molecules, upload_molecules)


client = TestClient(app)


@mark.skip(reason="no way of currently testing cache")
def test_caching_search_molecules():
    def search_request(query: str, source: str):
        response = client.get(f"/search/{query}")
        assert response.status_code == 200
        data = response.json()
        assert "source" in data
        assert data["source"] == source
        return data["data"]

    query = "c1ccccc1"
    data = search_request(query, "database")
    assert redis_client.exists(f"search:{query}")
    sleep(60-0.1)
    assert data == search_request(query, "cache")
    sleep(0.2)
    assert not redis_client.exists(f"search:{query}")
    search_request(query, "database")


@mark.skip(reason="no way of currently testing this")
def test_retrieve_all_molecules():
    response = client.get("/smiles/")
    assert response.status_code == 200
    # assert response.json() == []


def test_get_server():
    response = client.get("/")
    assert response.status_code == 200
    assert "server_id" in response.json()

  
# def test_add_molecule_smiles():
#     pass
# def test_retrieve_molecule_by_id():
#     pass
# def test_update_molecule():

# def test_delete_molecule():

# def test_search_molecules():

# def test_upload_molecules():

# Note that relative imports are based on the name of the current module. Since 
# the name of the main module is always "__main__", modules intended for use as 
# the main module of a Python application must always use absolute imports.