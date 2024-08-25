# from src.main import Molecule
# from app.dao.base import BaseDAO
from typing import List, Self
from sqlalchemy import create_engine, URL, String, exc
from sqlalchemy import select, insert, text
from sqlalchemy.orm import (Session, DeclarativeBase, Mapped, 
                            mapped_column)  # , relationship

url_object = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="kx@jj5/g",  # plain (unescaped) text
    host="localhost",
    database="molecules",
)

# engine = create_engine(url_object)
# engine = create_engine("postgresql+psycopg2://" 
#                        "scott:tiger@localhost:5432/mydatabase")
# dialect+driver://username:password@host:port/database
engine = create_engine("sqlite:///..\\..\\SMILESstorage.db")
# , echo=True)


class Base(DeclarativeBase):
    pass


# table structure
class Molecules(Base):
    __tablename__ = "molecules"
    id: Mapped[int] = mapped_column(primary_key=True)
    smiles: Mapped[str] = mapped_column(String(2778), nullable=False)
    
    def __repr__(self) -> str:
        return f"<{self.id!r}. {self.smiles!r}>"


Molecules.metadata.create_all(engine, checkfirst=True)


'''
Just as a matter of curiosity, the longest SMILES string created so far
is a complex yet discrete cluster with 52 metallic atoms and a SMILES
string of 2778 characters.
'''

""" 
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
 """
class BaseDAO:
    model = None
    
    @classmethod
    def create(cls, **data: dict) -> None:
        new_object = cls.model(**data)
        # create session and add objects
        with Session(engine) as session, session.begin():
            session.add(new_object)
        # inner context calls session.commit(), if there were no exceptions
        # outer context calls session.close()
    
    @classmethod
    def all(cls) -> Molecules:
        # create session and get objects
        with Session(engine) as session:  # , session.begin():
            result = session.scalars(select(cls.model)).all()
        # context calls session.close()
        return result
    
    @classmethod
    def get(cls, **data: dict) -> Self:
        """
        Create session and get exactly one scalar result or
        raise an exception.

        Raises [NoResultFound](https://docs.sqlalchemy.org/en/20/core/exceptions.html#sqlalchemy.exc.NoResultFound)
        if the result returns no rows, or
        [MultipleResultsFound](https://docs.sqlalchemy.org/en/20/core/exceptions.html#sqlalchemy.exc.MultipleResultsFound)
        if multiple rows would be returned.
        """
        # sqlalchemy.exc.NoResultFound: No row was found when one was required
        # sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when exactly one was required
        with Session(engine) as session:  # , session.begin():
            query = select(cls.model).filter_by(**data)
            result = session.scalars(query).one()
        # context calls session.close()
        return result

        # result = cls.filter(**data).scalar_one()

    @classmethod
    def filter(cls, **data: dict) -> Molecules:
        # create session and get objects
        with Session(engine) as session:  # , session.begin():
            query = select(cls.model).filter_by(**data)
            result = session.scalars(query).all()
        # context calls session.close()
        return result
    
    @classmethod
    def delete(cls, id: int) -> Molecules:
        """ create session and delete objects """
        with Session(engine) as session, session.begin():
            item = session.get_one(cls.model, id)
            """
            Return exactly one instance based on the given primary key identifier, or raise an exception if not found.

            Raises sqlalchemy.orm.exc.NoResultFound if the query selects no rows. """
            # sqlalchemy.exc.NoResultFound: No row was found when one was required
            session.delete(item)
        # context calls session.close()
        return item
    

class MoleculeDAO(BaseDAO):
    model = Molecules
       
    @classmethod
    def smiles(cls) -> List[str]:
        """ Get stored SMILES strings """
        with Session(engine) as session, session.begin():
            result = session.scalars(select(cls.model.smiles)).all()
        # context calls session.close()
        return result
    
    @classmethod
    def insert(cls, *smiles: str) -> Molecules | int:
        """
        - Store one `smiles` string of a chemical compound.
        
        - Store many `smiles` strings as arguments separated by ` , `.
        """
        with Session(engine) as session, session.begin():
            values = [{'smiles': s} for s in smiles]
            statement = insert(cls.model).values(values).returning(cls.model)
            result = session.execute(statement).all()
            # session.add(instance)
        # inner context calls session.commit(), if there were no exceptions
        # outer context calls session.close()
        # return result
    
    @classmethod
    def update(cls, id: int, smiles: str) -> None:
        """ create session and update an object by id """
        with Session(engine) as session, session.begin():
            instance = session.get_one(cls.model, id)
            """
            Return exactly one instance based on the given primary key identifier, or raise an exception if not found.

            Raises sqlalchemy.orm.exc.NoResultFound if the query selects no rows. """
            # sqlalchemy.exc.NoResultFound: No row was found when one was required
            # session.update(instance)
            instance.smiles = smiles
            # session.add(instance)
        # inner context calls session.commit(), if there were no exceptions
        # outer context calls session.close()
        # return instance