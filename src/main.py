from typing import List
from rdkit import Chem
# from rdkit.Chem import Draw

def substructure_search(mols: List[str], mol: str) -> List[str]:
    """ 
    Function returns a list of all molecules as SMILES strings from mols 
    that contain substructure mol as SMILES string.
    """
    mol = Chem.MolFromSmiles(mol)
    return [smiles for smiles in mols if Chem.MolFromSmiles(smiles).HasSubstructMatch(mol)]
