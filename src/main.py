from typing import List
from rdkit import Chem
# from rdkit.Chem import Draw

def substructure_search(mols: List[str], mol: str) -> List[str]:
    """ 
    Function returns a list of all molecules as SMILES strings from mols 
    that contain substructure mol as SMILES string.
    """
    mol = Chem.MolFromSmiles(mol)
    return [smiles for smiles in mols 
            if Chem.MolFromSmiles(smiles).HasSubstructMatch(mol)]

if __name__ == "__main__":
    example = substructure_search(["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"], "c1ccccc1")
    # ["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"]
    print(example)