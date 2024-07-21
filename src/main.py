# from typing import Union, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Molecule(BaseModel):
    identifier: int
    smiles: str


def substructure_search(mols, mol):
    pass

app = FastAPI()

molecules = {}

@app.get("/")
@app.get("/molecules/")
def retrieve_all_molecules():
    return list(molecules.values())

@app.post("/molecules/", status_code=201)
def add_molecule_smiles(new: Molecule):
    if new.identifier in molecules:
        raise HTTPException(status_code=400, detail=f"The molecule with identifier {new.identifier} is found, duplicate key raised an IntegrityError")
    else:
        molecules[new.identifier] = new
        return molecules[new.identifier]


@app.get("/molecules/{identifier}")
def retrieve_molecule_by_id(identifier: int):
    if identifier in molecules:
        return molecules[identifier]
    raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

@app.put("/molecules/{identifier}")
def update_molecule(identifier: int, updated: Molecule):
    if identifier != updated.identifier:
        raise HTTPException(status_code=400, detail=f"The molecule identifiers {identifier} != {updated.identifier} do not match.")
    elif identifier in molecules:
        molecules[identifier] = updated
        return molecules[identifier]
    else:
        raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

@app.delete("/molecules/{identifier}")
def delete_molecule(identifier: int):
    if identifier in molecules:        
        return molecules.pop(identifier)
    else:
        raise HTTPException(status_code=404, detail=f"The molecule with identifier {identifier} is not found.")

# Substructure search for all added molecules
# [Optional] Upload json file with molecules

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)