# from typing import List, Generator  # , Union, Optional
from rdkit.Chem import MolFromSmiles  # , Draw
from fastapi import FastAPI, status, HTTPException, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, NoResultFound  # , SQLAlchemyError
from os import getenv
from src.dao import MoleculeDAO
from src.logger import logger
from src.middleware import log_middleware
from src.caching import redis_client, get_cached_result, set_cache
from src.tasks import substructure_search_task, substructure_search
from src.celery_worker import celery
from celery.result import AsyncResult


class Molecule(BaseModel):
    identifier: int
    smiles: str


app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
logger.info("Started uvicorn web container " + getenv("SERVER_ID", "1"))


@app.get("/", summary='Check nginx load balancing', tags=['Load balancer'])
def get_server():
    """
    You should be able to access the application on your browser.
    Confirm that the load balancer distributes the request to both
    web containers.
    """
    return {"server_id": getenv("SERVER_ID", "1")}


@app.get("/tasks/{task_id}", tags=['Substructure search'])
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    task = {"task_id": task_id, "status": task_result.state}
    if task_result.state == 'STARTED':
        task["status"] = "Task is still processing"
    elif task_result.successful() or task_result.state == 'SUCCESS':
        task["status"] = "Task completed"
        task["result"] = task_result.result
    return task


@app.get("/smiles/", tags=['Checking stored molecule SMILES'])
def retrieve_all_molecules(limit: int = 100, offset: int = 0):
    '''
    Beginning from *offset, limit* the number of molecules in the response.
    '''
    return MoleculeDAO.all(limit, offset)


@app.post("/smiles/", status_code=status.HTTP_201_CREATED,
          tags=['Storing molecule SMILES'])
def add_molecule_smiles(smiles: str):
    if MolFromSmiles(smiles) is None:
        raise HTTPException(
            status_code=400,
            detail=("SMILES Parse Error: syntax error "
                    f"for input '{smiles}'.")
                    )
    else:
        try:
            MoleculeDAO.create(smiles=smiles)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Molecule with this SMILES value already exists"
                )
            # raise HTTPException(
            #     status_code=400,
            #     detail=("The molecule is found, duplicate raised "
            #             "an IntegrityError: UNIQUE constraint failed")
            #             )
        else:
            return MoleculeDAO.last(smiles=smiles)


@app.get("/smiles/{identifier}", tags=['Checking stored molecule SMILES'])
def retrieve_molecule_by_id(identifier: int):
    try:
        instance = MoleculeDAO.get(id=identifier)
    except NoResultFound as e:
        print(e)
        raise HTTPException(
            status_code=404,
            detail=f"The molecule with identifier {identifier} is not found."
            )
    else:
        return instance


@app.put("/smiles/{identifier}", tags=['Storing molecule SMILES'])
def create_update_molecule(identifier: int, updated: Molecule):
    if identifier != updated.identifier:
        raise HTTPException(
            status_code=400,
            detail=("The molecule identifiers do not match. "
                    f"{identifier} != {updated.identifier}")
                )
    if MolFromSmiles(updated.smiles) is None:
        raise HTTPException(
            status_code=400,
            detail=("SMILES Parse Error: syntax error "
                    f"for input: {updated.smiles}")
                )
    try:
        MoleculeDAO.update(id=identifier, smiles=updated.smiles)
    except NoResultFound as e:
        print(e)
        MoleculeDAO.create(id=identifier, smiles=updated.smiles)
        # TODO: 201 Created
    finally:
        return MoleculeDAO.get(id=identifier)


@app.delete("/smiles/{identifier}", tags=['Storing molecule SMILES'],
            response_description="The molecule is deleted",
            summary="Delete a molecule from storage by identifier")
def delete_molecule(identifier: int):
    try:
        instance = MoleculeDAO.delete(id=identifier)
    except NoResultFound as e:
        print(e)
        raise HTTPException(
            status_code=404,
            detail=("The molecule with identifier "
                    f"{identifier} is not found.")
            )
    else:
        return instance


@app.get("/search/{mol}", tags=['Substructure search'])
def search_molecules(mol: str = None, max_num: int = 0,
                     limit: int = 100, offset: int = 0,
                     no_cache: bool = False):
    """
    Substructure search for all added molecules

    - **mol**: a unique SMILES string for this substructure molecule,
    - **return** a list of all molecules that contain
    substructure `mol` as SMILES strings
    - get the first **max_num** chemical compounds
    that contain substructure `mol`
    - specifying **no_cache** in any other case variation
    as True, true, on, yes, 1 will delete the cache
    """
    cache_key = f"search:{mol}"
    if no_cache:
        redis_client.delete("SMILES", cache_key)
    if redis_client.exists("SMILES"):
        molecules = get_cached_result("SMILES")
        logger.debug("get_cached SMILES")
    else:
        molecules = MoleculeDAO.smiles(limit, offset)
        set_cache("SMILES", molecules, 5*60)
        logger.debug("set_cache SMILES")
    if len(molecules) < 1 or mol is None:
        raise HTTPException(
            status_code=400,
            detail="The molecules for substructure search aren't provided"
            )
    if redis_client.exists(cache_key):
        return {"source": "cache", "data": get_cached_result(cache_key)}
    if max_num <= 0:
        chemical_compounds = list(substructure_search(molecules, mol))
    else:
        num = 0
        chemical_compounds = []
        for compound in substructure_search(molecules, mol):
            chemical_compounds.append(compound)
            num += 1
            if num == max_num:
                break
    search_result = {"query": mol, "result": chemical_compounds}
    set_cache(cache_key, search_result)
    # sets an expiration of 60s
    return {"source": "database", "data": search_result}


@app.post("/search/{smiles}", tags=['Substructure search'])
async def create_task(smiles: str):
    """
    ### Modify the substructure search functionality to use Celery.
    Send a POST request to add a search task

    Check for cached search result in **Redis** before searching.
    - If found, return it immediately.
    - If the result is not cached, 
        1. Send a request to **Celery** to start the
        `substructure search task`,
        2. You will receive a response with the task_id.
        To check the status of the task `/tasks/{task_id}`.
        2. It performs the search, caches the result,
        3. and then you can send request to get results by task url.
    """
    if MolFromSmiles(smiles) is None:
        raise HTTPException(
            status_code=400,
            detail=("SMILES Parse Error: syntax error "
                    f"for input '{smiles}'.")
                    )
    cache_key = f"search:{smiles}"
    result = get_cached_result(cache_key)
    if result is None:
        task = substructure_search_task.delay(smiles)
        link = getenv("DOMAIN", "http://localhost")
        link += app.url_path_for("get_task_result", task_id=task.id)
        return {"task_id": task.id, "status": task.status, "link": link}
    return {"source": "cache search", "data": result}


@app.post("/molecules/", status_code=status.HTTP_201_CREATED,
          summary="[Optional] Upload file with molecules",
          tags=['Substructure search'])
async def upload_molecules(file: UploadFile | None = None):
    #   , n: int = float('inf'), start: int = 1):
    """
    *[Optional]*
    ---
    Upload a text `file` with molecules as SMILES strings on separate lines.
    """
    # Upload `n` molecules and add smiles to container
    # starting from identifier `start`
    if file is None:
        upload = ["CCO", "c1ccccc1", "Cc1ccccc1", "C(=O)O",
                  "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"]
    elif (file.filename.endswith(('.txt')) and
          file.content_type == 'text/plain'):
        upload = await file.read()
        upload = upload.decode('utf-8').replace('\r', '').split('\n')
    else:
        raise HTTPException(
            status_code=400,
            detail="Upload a text file with molecules as SMILES strings."
            )
    smiles = []
    for s in upload:
        s = s.strip()
        if s and s not in smiles and MolFromSmiles(s) is not None:
            smiles.append(s)
    MoleculeDAO.insert(*smiles)
    return MoleculeDAO.last(limit=len(smiles))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
