from src.celery_worker import celery
from src.caching import redis_client, get_cached_result, set_cache
from src.dao import MoleculeDAO
from src.logger import logger
from typing import List, Generator
from rdkit.Chem import MolFromSmiles  # , Draw


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


@celery.task
def substructure_search_task(smiles):
    # Get all stored chemical compounds
    source = "database"
    molecules = get_cached_result("SMILES")
    if molecules is None:
        molecules = MoleculeDAO.smiles()
        set_cache("SMILES", molecules, 5*60)
        logger.debug("set_cache SMILES")
    else:
        source = "cache"
        logger.debug("get_cached SMILES")
    cache_key = f"search:{smiles}"
    chemical_compounds = list(substructure_search(molecules, smiles))
    search_result = {"query": smiles, "result": chemical_compounds}
    set_cache(cache_key, search_result)
    # sets an expiration of 60s
    return {"source": source, "data": search_result}
