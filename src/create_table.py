# import sqlalchemy as sa
from src.dao import engine, Molecules


def upgrade() -> None:
    Molecules.metadata.create_all(engine, checkfirst=True)


def downgrade() -> None:
    Molecules.drop(engine)


if __name__ == "__main__":
    upgrade()