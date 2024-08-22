from .main import Molecule
from app.dao.base import BaseDAO

from sqlalchemy import create_engine, URL, String
from sqlalchemy import select, text
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column  # , relationship

url_object = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="kx@jj5/g",  # plain (unescaped) text
    host="localhost",
    database="molecules",
)

# engine = create_engine(url_object)
# engine = create_engine("postgresql+psycopg2://scott:tiger@localhost:5432/mydatabase")
# dialect+driver://username:password@host:port/database
engine = create_engine("sqlite:///..\\..\\SMILESstorage.db", echo=True)


class Base(DeclarativeBase):
    pass



class Molecules(Base):
    __tablename__ = "molecules"
    id: Mapped[int] = mapped_column(primary_key=True)
    smiles: Mapped[str] = mapped_column(String(2778), nullable=False)
    
    def __repr__(self) -> str:
        return f"{self.id!r}. {self.smiles!r}"

# Molecules.__repr__ = lambda self: f"{self.id!r}. {self.smiles!r}"
Molecules.metadata.create_all(engine, checkfirst=True)


'''
Just as a matter of curiosity, the longest SMILES string created so far
is a complex yet discrete cluster with 52 metallic atoms and a SMILES
string of 2778 characters.
'''


with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO molecules (smiles) VALUES (:x);"),
        [{"x": "y"}, {"x": "pourquie"}],
    )
    ql = conn.execute(
        text("SELECT * FROM molecules;")
    )
    for q in ql:
        print(q)




#    conn.execute(sqlalchemy.text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
        sqlalchemy.text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )

# from src.main import Molecule

class BaseDAO:
    model = None
    
    @classmethod
    def create(cls, **data: dict):
        new_object = cls.model(**data)
        # create session and add objects
        with Session(engine) as session, session.begin():
            session.add(new_object)
        # inner context calls session.commit(), if there were no exceptions
        # outer context calls session.close()
    
    @classmethod
    def all(cls):
        # create session and get objects
        with Session(engine) as session:  # , session.begin():
            result = session.scalars(select(cls.model)).all()
        # context calls session.close()
        return result
    
    @classmethod
    def get(cls, **data: dict): TODO
        # create session and get objects
        with Session(engine) as session:  # , session.begin():
            result = session.scalars(select(cls.model)).all()
        # context calls session.close()
        return result


class MoleculeDAO(BaseDAO):
    model = Molecules
    # identifier: int
    # smiles: str

#######

    @classmethod
    async def find_all_drugs(cls):
            return drugs.scalars().all()

    @classmethod
    async def find_full_data(cls, drug_id):
        async with async_session_maker() as session:
            # Query to get drug info
            query = select(cls.model).filter_by(id=drug_id)
            result = await session.execute(query)
            drug_info = result.scalar_one_or_none()

            # If drug is not found, return None
            if not drug_info:
                return None

            drug_data = drug_info.to_dict()
            return drug_data


    @classmethod
    async def delete_drug_by_id(cls, drug_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                query = select(cls.model).filter_by(id=drug_id)
                result = await session.execute(query)
                drug_to_delete = result.scalar_one_or_none()

                if not drug_to_delete:
                    return None

                # Delete the drug
                await session.execute(delete(cls.model).filter_by(id=drug_id))

                await session.commit()
                return drug_id


