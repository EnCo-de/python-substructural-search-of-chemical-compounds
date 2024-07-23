from typing import List # , Union, Optional
from rdkit.Chem import MolFromSmiles # , Draw
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

def substructure_search(mols: List[str], mol: str) -> List[str]:
    """ 
    Function returns a list of all molecules as SMILES strings from mols 
    that contain substructure mol as SMILES string.
    """
    mol = MolFromSmiles(mol)
    return [smiles for smiles in mols 
            if MolFromSmiles(smiles).HasSubstructMatch(mol)]


class Molecule(BaseModel):
    identifier: int
    smiles: str


app = FastAPI()

molecules = {}

@app.get("/")
@app.get("/smiles/")
def retrieve_all_molecules():
    return list(molecules.values())

@app.post("/smiles/", status_code=201)
def add_molecule_smiles(new: Molecule):
    if new.identifier in molecules:
        raise HTTPException(status_code=400, detail=f"The molecule with identifier {new.identifier} is found, duplicate key raised an IntegrityError")
    else:
        molecules[new.identifier] = new
        return molecules[new.identifier]

@app.get("/smiles/{identifier}")
def retrieve_molecule_by_id(identifier: int):
    if identifier in molecules:
        return molecules[identifier]
    raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

@app.put("/smiles/{identifier}")
def update_molecule(identifier: int, updated: Molecule):
    if identifier != updated.identifier:
        raise HTTPException(status_code=400, detail=f"The molecule identifiers {identifier} != {updated.identifier} do not match.")
    elif identifier in molecules:
        molecules[identifier] = updated
        return molecules[identifier]
    else:
        raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

@app.delete("/smiles/{identifier}")
def delete_molecule(identifier: int):
    if identifier in molecules:        
        return molecules.pop(identifier)
    else:
        raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

# Substructure search for all added molecules
# [Optional] Upload json file with molecules


if __name__ == "__main__":
    import uvicorn

    example = substructure_search(["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"], "c1ccccc1")
    assert example == ["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"]
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
