from dao import MoleculeDAO

# z = MoleculeDAO.create(smiles='GUESS')
# print(z)
# z = MoleculeDAO.create(id=7, smiles='Buzz')
# print(MoleculeDAO.delete(7))
# s = MoleculeDAO.get(id=2)
# print(type(s), s)
s = MoleculeDAO.all()
print(type(s), s)
# for x in s:
#     print(type(x), x)
MoleculeDAO.insert('Hugo Boss')
MoleculeDAO.insert('Louis', 'Viton', 'Chu')

print(MoleculeDAO.filter(smiles='y'))
print(MoleculeDAO.get(id=3, smiles='y'))
MoleculeDAO.update(id=20, smiles='Hermes')
# print()
print(MoleculeDAO.get(smiles='Yeah'))
print(MoleculeDAO.all())
print(MoleculeDAO.smiles())
# s = MoleculeDAO.get(id=22)
