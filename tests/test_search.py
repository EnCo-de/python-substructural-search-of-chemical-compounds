# from typing import List # , Union, Optional
# from rdkit.Chem import MolFromSmiles # , Draw
# from fastapi import FastAPI, status, HTTPException
# from pydantic import BaseModel
# from os import getenv
from pytest import mark, fixture
from src.main import (substructure_search, app, get_server, retrieve_all_molecules, 
                   add_molecule_smiles, retrieve_molecule_by_id, update_molecule, 
                   delete_molecule, search_molecules, upload_molecules)

def test_substructure_search():
    example = substructure_search(
        ["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"], 
        "c1ccccc1")
    assert example == ["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"]
    assert substructure_search(["c1ccccc1"], "not-SMILES") == []
    assert substructure_search(["not-SMILES","CC(=O)Oc1ccccc1C(=O)O","not-SMILES","not-SMILES"], "c1ccccc1") == ["CC(=O)Oc1ccccc1C(=O)O"]

@mark.parametrize("mols, mol, expected", [
    (["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"],'H-H',[]),
    (["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"],'C(=O)O',["CC(=O)Oc1ccccc1C(=O)O"]),
    (["CCO", "c1ccccc1", "CC(=O)O"], '',  []),
    ([], "CCO",  []),
    # ("CCOc1ccccc1", 'O',  ["CCO", "CC(=O)O"]),
    (["CCO", "c1ccccc1", "CC(=O)O", "C"], 'O',  ["CCO", "CC(=O)O"]),
    ])
def test_parametrize_search(mols, mol, expected):
    assert substructure_search(mols, mol) == expected

@fixture
def molecules_storage():
    return {1: "CC(=O)Oc1ccccc1C(=O)O"}

@mark.xfail(raises=AssertionError)
def test_substructure_str():
    assert substructure_search("CC(=O)Oc1ccccc1C(=O)O", "C") == ["C"]

@mark.xfail(raises=AssertionError, reason="known issue SMILES Parse Error, to be fixed")
def test_function():
    mols = 'CCOc1ccccc1'
    mol = 'O'
    expected = ['CCO', 'CC(=O)O']
    assert substructure_search(mols, mol) == expected
    assert substructure_search("CC(=O)Oc1ccccc1C(=O)O", "C") == ["C"]
    