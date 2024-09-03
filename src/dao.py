from os import getenv
from typing import List
from sqlalchemy import create_engine, URL, String
from sqlalchemy import select, insert  # , text, exc
from sqlalchemy.orm import (Session, DeclarativeBase, Mapped,
                            mapped_column)  # , relationship
from src.logger import logger

url_object = URL.create(
    "postgresql+psycopg",
    username=getenv("DB_USER", "postgres"),
    password=getenv("DB_PASSWORD", "kx@jj5/g"),  # plain (unescaped) text
    host=getenv("DB_HOST", "localhost"),
    database=getenv("DB_NAME", "compounds"),
)

# url_object = URL.create(
#     "postgresql+psycopg2",
#     username="postgres",
#     password="kx@jj5/g",  # plain (unescaped) text
#     host="localhost",
#     database="molecules",
# )

# engine = create_engine("postgresql+psycopg2://"
#                        "scott:tiger@localhost:5432/mydatabase")
# dialect+driver://username:password@host:port/database
if getenv("DB_HOST") == 'postgres':
    engine = create_engine(url_object)
else:
    engine = create_engine("sqlite:///..\\..\\SMILESstorage.db")
    # , echo=True)
logger.debug(url_object, engine)


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
    def all(cls, limit: int = 100, offset: int = 0) -> Molecules:
        '''
        You can change the query to get at maximum
        some number of results with *`limit`*.

        And the same way, you can skip the
        first results with *`offset`*.
        '''
        # create session and get objects
        with Session(engine) as session:  # , session.begin():
            statement = select(cls.model).offset(offset).limit(limit)
            results = session.scalars(statement).all()
        # context calls session.close()
        return results

    @classmethod
    def get(cls, **data: dict):
        """
        Create session and get exactly one scalar result or
        raise an exception.

        Raises
        [NoResultFound](https://docs.sqlalchemy.org/en/20/core/exceptions.html#sqlalchemy.exc.NoResultFound)
        if the result returns no rows, or
        [MultipleResultsFound](https://docs.sqlalchemy.org/en/20/core/exceptions.html#sqlalchemy.exc.MultipleResultsFound)
        if multiple rows would be returned.
        """
        # sqlalchemy.exc.NoResultFound: No row was found when one was required
        # sqlalchemy.exc.MultipleResultsFound: Multiple rows were found
        # when exactly one was required
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
    def last(cls, limit: int = 1, **data: dict) -> Molecules:
        # create session and get objects
        with Session(engine) as session:  # , session.begin():
            query = (select(cls.model).filter_by(**data)
                     .order_by(cls.model.id.desc())
                     .limit(limit))
            if limit > 1:
                result = session.scalars(query).all()
            elif limit == 1:
                result = session.scalars(query).one()
        # context calls session.close()
        return result

    @classmethod
    def delete(cls, id: int) -> Molecules:
        """ create session and delete objects """
        with Session(engine) as session, session.begin():
            item = session.get_one(cls.model, id)
            """
            Return exactly one instance based on the given primary
            key identifier, or raise an exception if not found.

            Raises sqlalchemy.orm.exc.NoResultFound if the query
            selects no rows. """
            # sqlalchemy.exc.NoResultFound: No row was found
            # when one was required
            session.delete(item)
        # context calls session.close()
        return item


class MoleculeDAO(BaseDAO):
    model = Molecules

    @classmethod
    def smiles(cls, limit: int = 100, offset: int = 0) -> List[str]:
        """ Get stored SMILES strings

        You can change the query to get at maximum
        some number of results with *`limit`*.

        And the same way, you can skip the
        first results with *`offset`*.
        """
        with Session(engine) as session, session.begin():
            statement = (select(cls.model.smiles)
                         .offset(offset)
                         .limit(limit))
            results = session.scalars(statement).all()
        # context calls session.close()
        return results

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
            return result
        # inner context calls session.commit(), if there were no exceptions
        # outer context calls session.close()

    @classmethod
    def update(cls, id: int, smiles: str) -> None:
        """ create session and update an object by id """
        with Session(engine) as session, session.begin():
            instance = session.get_one(cls.model, id)
            """
            Return exactly one instance based on the given
            primary key identifier, or raise an exception if not found.

            Raises sqlalchemy.orm.exc.NoResultFound if the query
            selects no rows. """
            # sqlalchemy.exc.NoResultFound: No row was found
            # when one was required
            # session.update(instance)
            instance.smiles = smiles
            # session.add(instance)
        # inner context calls session.commit(), if there were no exceptions
        # outer context calls session.close()
        # return instance
