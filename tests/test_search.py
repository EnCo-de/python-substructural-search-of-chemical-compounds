from pytest import mark, fixture, raises
from src.tasks import substructure_search


@fixture
def molecules_storage():
    return ["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"]


def test_substructure_search(molecules_storage):
    example = list(substructure_search(molecules_storage, "c1ccccc1"))
    assert example == ["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"]
    assert list(substructure_search(molecules_storage, "not-SMILES")) == []
    assert list(substructure_search(
        ["not-SMILES","CC(=O)Oc1ccccc1C(=O)O","not-SMILES","not-SMILES"],
        "c1ccccc1")) == ["CC(=O)Oc1ccccc1C(=O)O"]
    expected = ['CCO', 'CC(=O)O']
    assert list(substructure_search(tuple(expected), "O")) == expected


@mark.parametrize("mols, mol, expected", [
    (["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"],'H-H',[]),
    (["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"],'C(=O)O',
     ["CC(=O)Oc1ccccc1C(=O)O"]),
    (["CCO", "c1ccccc1", "CC(=O)O"], '',  []),
    ([], "CCO",  []),
    (["CCO", "c1ccccc1", "CC(=O)O", "C"], 'O',  ["CCO", "CC(=O)O"]),
    ])
def test_parametrize_search(mols, mol, expected):
    assert list(substructure_search(mols, mol)) == expected


@mark.xfail(reason="SMILES Parse Error")
def test_substructure_str():
    assert list(substructure_search(["CC(=O)Oc1ccccc1C(=O)O"],
                                    "C2(OH)4")) == ["C"]


@mark.skip(reason="no way of currently testing this")
def test_skip():
    print("Skip this test function")


@mark.xfail(
        raises=TypeError,
        reason=("TypeError: No converter to C++"
                "value from NoneType object")
        )
def test_substructure_none(molecules_storage):
    assert list(substructure_search(molecules_storage, None)) == ["C"]


def test_function_raises_exceptions_str_input():
    mols = 'CCOc1ccccc1'
    mol = 'O'
    expected = ['CCO', 'CC(=O)O']
    # reason="Wrong argument data type"
    with raises(TypeError, match='input value'):
        next(substructure_search(mols, mol))
    with raises(TypeError, match='input value'):
        next(substructure_search("CC(=O)Oc1ccccc1C(=O)O", "C"))


def test_function_raises_exceptions_int_input(molecules_storage):
    with raises(TypeError, match='input value'):
        molecules_storage.extend([1, 2, 3])
        next(substructure_search(molecules_storage, "C"))


def test_function_raises_exceptions_no_args(molecules_storage):
    with raises(TypeError, match=r'missing \d required positional argument'):
        substructure_search()
    with raises(TypeError, match=r'missing \d required positional argument'):
        substructure_search(molecules_storage)