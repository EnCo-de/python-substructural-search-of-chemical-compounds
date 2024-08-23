from dao import MoleculeDAO

s = MoleculeDAO.get(id=2)
print(type(s), s)
s = MoleculeDAO.all()
print(type(s), s)
for x in s:
    print(type(x), x)
print(MoleculeDAO.filter(smiles='y'))
print(MoleculeDAO.smiles())
print(MoleculeDAO.get(smiles='Yeah'))
# s = MoleculeDAO.get(id=22)
