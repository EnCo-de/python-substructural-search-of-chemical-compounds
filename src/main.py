from typing import List # , Union, Optional
from rdkit.Chem import MolFromSmiles # , Draw
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel

def substructure_search(mols: List[str], mol: str) -> List[str]:
    """ 
    Find and return a list of all molecules as SMILES strings from *mols* 
    that contain substructure *mol* as SMILES string.
    """
    try:
        mol = MolFromSmiles(mol)
        if mol is None:
            return []
        return [smiles for smiles in mols 
            if MolFromSmiles(smiles).HasSubstructMatch(mol)]
    except:
        return []


class Molecule(BaseModel):
    identifier: int
    smiles: str


app = FastAPI()

molecules = {}

@app.get("/", tags=['Checking stored molecule SMILES'])
@app.get("/smiles/", tags=['Checking stored molecule SMILES'])
def retrieve_all_molecules():
    return list(molecules.values())

@app.post("/smiles/", status_code=status.HTTP_201_CREATED, tags=['Storing molecule SMILES'])
def add_molecule_smiles(new: Molecule):
    if new.identifier in molecules:
        raise HTTPException(status_code=400, detail=f"The molecule with identifier {new.identifier} is found, duplicate key raised an IntegrityError")
    else:
        if MolFromSmiles(new.smiles) is None:
            raise HTTPException(status_code=400, detail=f"SMILES Parse Error: syntax error for input: {new.smiles}")
        molecules[new.identifier] = new
        return molecules[new.identifier]

@app.get("/smiles/{identifier}", tags=['Checking stored molecule SMILES'])
def retrieve_molecule_by_id(identifier: int):
    if identifier in molecules:
        return molecules[identifier]
    raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

@app.put("/smiles/{identifier}", tags=['Storing molecule SMILES'])
def update_molecule(identifier: int, updated: Molecule):
    if identifier != updated.identifier:
        raise HTTPException(status_code=400, detail=f"The molecule identifiers {identifier} != {updated.identifier} do not match.")
    elif identifier in molecules:
        if MolFromSmiles(updated.smiles) is None:
            raise HTTPException(status_code=400, detail=f"SMILES Parse Error: syntax error for input: {updated.smiles}")
        molecules[identifier] = updated
        return molecules[identifier]
    else:
        raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

@app.delete("/smiles/{identifier}", response_description="The molecule is deleted",
            summary="Delete a molecule from storage by identifier", 
            tags=['Storing molecule SMILES'])
def delete_molecule(identifier: int):
    if identifier in molecules:        
        return molecules.pop(identifier)
    else:
        raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

@app.get("/search/{mol}", tags=['Substructure search'])
def search_molecules(mol: str = None):
    """ 
    Substructure search for all added molecules 

    - **mol**: a unique SMILES string for this substructure molecule,
    - **return** a list of all molecules that contain substructure _mol_ as SMILES strings
    """
    if len(molecules) > 0 and mol is not None:
        mols = [molecule.smiles for molecule in molecules.values()]
        return substructure_search(mols, mol)
    else:
        raise HTTPException(status_code=400, detail=f"The molecules aren't provided for substructure search.")

@app.post("/molecules/", status_code=status.HTTP_201_CREATED, tags=['Substructure search'])
def upload_molecules(n: int = float('inf'), start: int = 1):
    """ [Optional] Upload n molecules and add smiles to container starting from identifier start """
    upload = ["CCO", "c1ccccc1", "Cc1ccccc1", "C(=O)O", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"]
    i = start
    while i - start < len(upload) and i - start <= n:
        molecules[i] = Molecule(identifier=i, smiles=upload[i - start])
        i += 1
    return list(molecules.values())


if __name__ == "__main__":
    import uvicorn

    example = substructure_search(
        ["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"], 
        "c1ccccc1")
    assert example == ["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"]
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
