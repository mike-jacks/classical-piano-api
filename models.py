from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship, declarative_base
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, CheckConstraint

metadata = MetaData()

Base: DeclarativeBase = declarative_base(metadata=metadata)

# Modlels and Tables
class PieceTable(Base):
    __tablename__ = "piece"
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    alt_name: Mapped[str | None]
    difficulty: Mapped[int] = mapped_column(CheckConstraint('difficulty BETWEEN 1 AND 10'), nullable=False)
    composer_id: Mapped[int] = mapped_column(ForeignKey("composer.id"), nullable=False)

    composer: Mapped['ComposerTable'] = relationship("ComposerTable", back_populates="pieces")

    def __repr__(self) -> str:
        return f"Piece(id={self.id!r}, name={self.name!r}, alt_name={self.alt_name!r}, difficulty={self.difficulty!r}, composer_id={self.composer_id!r})"
    
class ComposerTable(Base):
    __tablename__ = "composer"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    home_country: Mapped[str] = mapped_column(nullable=False)

    pieces: Mapped[list[PieceTable]] = relationship("PieceTable", back_populates='composer')

    def __repr__(self) -> str:
        return f"Composer(id={self.id!r}, name={self.name!r}, home_country={self.home_country!r})"


# Data Models
class ComposerModel(BaseModel):
    id: int
    name: str
    home_country: str
    pieces: list['PieceModel']

    class Config:
        orm_mode = True
        from_attributes = True

class PieceModel(BaseModel):
    id: int
    name: str
    alt_name: str | None
    difficulty: int
    composer_id:  int

    class Config:
        orm_mode = True
        from_attributes = True


# Requests

class CreateComposerRequest(BaseModel):
    name: str
    home_country: str

class UpdateComposerRequest(BaseModel):
    name: str | None = None
    home_country: str | None = None
    
class CreatePieceRequest(BaseModel):
    name: str
    alt_name: str | None = None
    difficulty: int
    composer_id: int

class UpdatePieceRequest(BaseModel):
    name: str | None = None
    alt_name: str | None = None
    difficulty: int | None = None
    composer_id: int | None = None
    


# Response Models
class GetComposersResponse(BaseModel):
    data: list[ComposerModel]
    detail: str

class GetPiecesResponse(BaseModel):
    data: list[PieceModel]
    detail: str
    
class CreateComposerResponse(BaseModel):
    data: ComposerModel
    detail: str

class UpdateComposerResponse(BaseModel):
    old_data: ComposerModel
    new_data: ComposerModel
    detail: str

class CreatePieceResponse(BaseModel):
    data: PieceModel
    detail: str

class UpdatePieceResponse(BaseModel):
    old_data: PieceModel
    new_data: PieceModel
    detail: str

class DeleteComposerResponse(BaseModel):
    data: ComposerModel
    detail: str

class DeletePieceResponse(BaseModel):
    data: PieceModel
    detail: str