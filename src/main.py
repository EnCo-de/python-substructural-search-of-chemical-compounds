# from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel


class Molecule(BaseModel):
    identifier: int
    smiles: str

    def to_json(self):
        return {'identifier': self.identifier, 'smiles': self.smiles}



def substructure_search(mols, mol):
    pass

app = FastAPI()

molecules = []

@app.get("/")
@app.get("/molecules/")
def retrieve_all_molecules():
    if molecules:
        n = max(molecules, key=lambda x: x.identifier)
        n = n.identifier
    else:
        n = 0
    molecules.append(Molecule(identifier=n+1, smiles='hooo'))
    return [item.to_json() for item in molecules]

@app.get("/molecules/{identifier}")
def retrieve_molecule_by_id(identifier: int):
    for molecule in molecules:
        if molecule.identifier == identifier:
            return {"molecule": molecule.to_json()}
    return {"404": "Not found"}