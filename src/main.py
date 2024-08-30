from typing import List, Generator  # , Union, Optional
from rdkit.Chem import MolFromSmiles  # , Draw
from fastapi import FastAPI, status, HTTPException, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, NoResultFound  # , SQLAlchemyError
from os import getenv
from src.dao import MoleculeDAO
from src.logger import logger
from src.middleware import log_process_time


def substructure_search(
        mols: List[str],
        mol: str
        ) -> Generator[str, None, None]:
    """
    Find and return a list of all molecules as SMILES strings from *`mols`*
    that contain substructure *`mol`* as SMILES string.
    """
    if not (isinstance(mols, (list, tuple)) and
            all(map(lambda x: isinstance(x, str), mols))):
        raise TypeError('an input value does not match the expected data type')
    mol = MolFromSmiles(mol)
    if mol is not None:
        for smiles in mols:
            if ((compound := MolFromSmiles(smiles)) and
                    compound.HasSubstructMatch(mol)):
                yield smiles


class Molecule(BaseModel):
    identifier: int
    smiles: str


app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_process_time)
# molecules = {}
logger.info("Started uvicorn web container")


@app.get("/", summary='Check nginx load balancing', tags=['Load balancer'])
def get_server():
    """
    You should be able to access the application on your browser.
    Confirm that the load balancer distributes the request to both
    web containers.
    """
    return {"server_id": getenv("SERVER_ID", "1")}


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
                     limit: int = 100, offset: int = 0):
    """
    Substructure search for all added molecules

    - **mol**: a unique SMILES string for this substructure molecule,
    - **return** a list of all molecules that contain
    substructure `mol` as SMILES strings
    - get the first **max_num** chemical compounds
    that contain substructure `mol`
    """
    molecules = MoleculeDAO.smiles(limit, offset)
    if len(molecules) < 1 or mol is None:
        raise HTTPException(
            status_code=400,
            detail="The molecules for substructure search aren't provided"
            )
    if max_num == 0:
        return list(substructure_search(molecules, mol))
    num = 0
    chemical_compounds = []
    for compound in substructure_search(molecules, mol):
        chemical_compounds.append(compound)
        num += 1
        if num == max_num:
            break
        return chemical_compounds


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
