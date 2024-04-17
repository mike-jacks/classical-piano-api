import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Base, ComposerTable, PieceTable

engine = create_engine("sqlite+pysqlite:///data/database.db", echo=True)

with open("composers.json", "r") as f:
    composers_list: list[dict] = json.load(f)

with open("pieces.json", "r") as f:
    piece_list: list[dict] = json.load(f)

Base.metadata.create_all(engine)

# Load json to database
with Session(bind=engine) as session:
    for composer in composers_list:
        composer_row = session.execute(select(ComposerTable).where(composer["composer_id"] == ComposerTable.id)).scalar_one_or_none()
        print(composer_row)
        if not composer_row:
            composer_row: ComposerTable = ComposerTable(id=composer["composer_id"], **{column: value for column, value in composer.items() if column in ComposerTable.__table__.columns and column != 'id'})
            session.add(composer_row)
    for piece in piece_list:
        piece_row: PieceTable = session.execute(select(PieceTable).where(piece["composer_id"] == PieceTable.composer_id)).scalar_one_or_none()
        if not piece_row:
            piece_row = PieceTable(**piece)
            session.add(piece_row)
    session.commit()