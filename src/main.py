# import io
from typing import List  # , Union, Optional
from rdkit.Chem import MolFromSmiles  # , Draw
from fastapi import FastAPI, status, HTTPException, UploadFile
from pydantic import BaseModel
from os import getenv


def substructure_search(mols: List[str], mol: str) -> List[str]:
    """
    Find and return a list of all molecules as SMILES strings from *`mols`*
    that contain substructure *`mol`* as SMILES string.
    """
    if not (isinstance(mols, (list, tuple, set)) and
            all(map(lambda x: isinstance(x, str), mols))):
        raise TypeError('an input value does not match the expected data type')
    mol = MolFromSmiles(mol)
    if mol is None:
        return []
    return [smiles for smiles in mols
            if (compound := MolFromSmiles(smiles)) and
            compound.HasSubstructMatch(mol)]


class Molecule(BaseModel):
    identifier: int
    smiles: str


app = FastAPI()

molecules = {}


@app.get("/", summary='Check nginx load balancing', tags=['Load balancer'])
def get_server():
    """
    You should be able to access the application on your browser.
    Confirm that the load balancer distributes the request to both
    web containers.
    """
    return {"server_id": getenv("SERVER_ID", "1")}


@app.get("/smiles/", tags=['Checking stored molecule SMILES'])
def retrieve_all_molecules():
    return list(molecules.values())


@app.post("/smiles/", status_code=status.HTTP_201_CREATED,
          tags=['Storing molecule SMILES'])
def add_molecule_smiles(new: Molecule):
    if new.identifier in molecules:
        raise HTTPException(
            status_code=400,
            detail=f"The molecule with identifier {new.identifier} \
                is found, duplicate key raised an IntegrityError"
                )
    else:
        if MolFromSmiles(new.smiles) is None:
            raise HTTPException(
                status_code=400,
                detail=f"SMILES Parse Error: syntax error \
                    for input: {new.smiles}"
                    )
        molecules[new.identifier] = new
        return molecules[new.identifier]


@app.get("/smiles/{identifier}", tags=['Checking stored molecule SMILES'])
def retrieve_molecule_by_id(identifier: int):
    if identifier in molecules:
        return molecules[identifier]
    raise HTTPException(
        status_code=404,
        detail=f"The molecule with identifier {identifier} is not found."
        )


@app.put("/smiles/{identifier}", tags=['Storing molecule SMILES'])
def update_molecule(identifier: int, updated: Molecule):
    if identifier != updated.identifier:
        raise HTTPException(
            status_code=400,
            detail=f"The molecule identifiers {identifier} \
                != {updated.identifier} do not match."
                )
    elif identifier in molecules:
        if MolFromSmiles(updated.smiles) is None:
            raise HTTPException(
                status_code=400,
                detail=f"SMILES Parse Error: syntax error \
                    for input: {updated.smiles}"
                    )
        molecules[identifier] = updated
        return molecules[identifier]
    else:
        raise HTTPException(
            status_code=404,
            detail=f"A molecule with identifier {identifier} is not found."
            )


@app.delete("/smiles/{identifier}", tags=['Storing molecule SMILES'],
            response_description="The molecule is deleted",
            summary="Delete a molecule from storage by identifier")
def delete_molecule(identifier: int):
    if identifier in molecules:
        return molecules.pop(identifier)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"The molecule with identifier \
                {identifier} is not found."
            )


@app.get("/search/{mol}", tags=['Substructure search'])
def search_molecules(mol: str = None):
    """
    Substructure search for all added molecules

    - **mol**: a unique SMILES string for this substructure molecule,
    - **return** a list of all molecules that contain 
    substructure `mol` as SMILES strings
    """
    if len(molecules) > 0 and mol is not None:
        mols = [molecule.smiles for molecule in molecules.values()]
        return substructure_search(mols, mol)
    else:
        raise HTTPException(
            status_code=400,
            detail="The molecules for substructure search aren't provided"
            )


@app.post("/molecules/", status_code=status.HTTP_201_CREATED, 
          summary="[Optional] Upload file with molecules", 
          tags=['Substructure search'])
async def upload_molecules(file: UploadFile | None = None, 
                           n: int = float('inf'), start: int = 1):
    """
    *[Optional]* Upload `n` molecules and add smiles to container
    starting from identifier `start`
    ---
    Upload a text `file` with molecules as SMILES strings on separate lines.
    """
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
            detail=f"Upload a text file with molecules as SMILES strings."
            )
    i = start
    end = min(len(upload), max(0, n)) + start
    while i < end:
        smiles = upload[i - start].strip()
        if smiles and MolFromSmiles(smiles) is not None:
            molecules[i] = Molecule(identifier=i, smiles=smiles)
        i += 1
    return list(molecules.values())


if __name__ == "__main__":
    import uvicorn

    example = substructure_search(
        ["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"],
        "c1ccccc1")
    assert example == ["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"]
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
