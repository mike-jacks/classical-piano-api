from fastapi import FastAPI, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db import engine
from models import (
    ComposerTable, PieceTable,
    ComposerModel, PieceModel,
    CreateComposerRequest, CreatePieceRequest,
    UpdateComposerRequest, UpdatePieceRequest,
    GetComposersResponse, GetPiecesResponse,
    CreateComposerResponse, CreatePieceResponse,
    UpdateComposerResponse, UpdatePieceResponse,
    DeleteComposerResponse, DeletePieceResponse
    )

app = FastAPI()

@app.get("/composers", tags=["composers"], response_model=GetComposersResponse, status_code=status.HTTP_200_OK)
async def get_composers() -> GetComposersResponse:
    with Session(bind=engine) as session:
        composers: list[ComposerTable]= session.execute(select(ComposerTable)).scalars().all()
        composer_data_list = [ComposerModel.model_validate(composer) for composer in composers]
        return GetComposersResponse(data=composer_data_list, detail="Composers fetched successfully.")

@app.get("/pieces", tags=["pieces"], response_model=GetPiecesResponse, status_code=status.HTTP_200_OK)
async def get_pieces(composer_id: int | None = None) -> GetPiecesResponse:
    with Session(bind=engine) as session:
        pieces: list[PieceTable] = session.execute(select(PieceTable)).scalars().all()
        piece_data_list = [PieceModel.model_validate(piece) for piece in pieces]
        if composer_id is not None:
            if not session.execute(select(ComposerTable).where(ComposerTable.id == composer_id)).scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Composer ID: {composer_id} not found.")
            piece_data_list = [piece for piece in piece_data_list if piece.composer_id == composer_id]
        return GetPiecesResponse(data=piece_data_list, detail="Pieces fetched successfully.")

@app.post("/composers", tags=["composers"], response_model=CreateComposerResponse, status_code=status.HTTP_201_CREATED)
async def add_composer(create_composer_request: CreateComposerRequest) -> CreateComposerResponse:
    with Session(bind=engine) as session:
        new_composer: ComposerTable = ComposerTable(**create_composer_request.model_dump())
        session.add(new_composer)
        session.commit()
        session.refresh(new_composer)
        composer_data = ComposerModel.model_validate(new_composer)
        return CreateComposerResponse(data=composer_data, detail="Composer added successfully.")

@app.post("/pieces", tags=["pieces"], response_model=CreatePieceResponse, status_code=status.HTTP_201_CREATED)
async def add_piece(create_piece_request: CreatePieceRequest) -> PieceModel:
    with Session(bind=engine) as session:
        composer: ComposerTable = session.execute(select(ComposerTable).where(ComposerTable.id == create_piece_request.composer_id)).scalar_one_or_none()
        if not composer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Composer ID: {create_piece_request.composer_id} not found.")
        new_piece = PieceTable(**create_piece_request.model_dump())
        session.add(new_piece)
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Difficulty is limited to the integers of 1 - 10 inclusively. Error: {error}")
        session.refresh(new_piece)
        piece_data = PieceModel.model_validate(new_piece)
        return CreatePieceResponse(data=piece_data, detail="Piece added successfully.")

@app.put("/composers/{composer_id}", tags=["composers"], response_model=UpdateComposerResponse, status_code=status.HTTP_200_OK) 
async def update_composer(composer_id: int, update_composer_request: UpdateComposerRequest) -> UpdateComposerResponse:
    with Session(bind=engine) as session:
        composer: ComposerTable = session.execute(select(ComposerTable).where(ComposerTable.id == composer_id)).scalar_one_or_none()
        if not composer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Composer ID: {composer_id} not found.")
        old_data = ComposerModel.model_validate(composer)
        composer.name = update_composer_request.name or composer.name
        composer.home_country = update_composer_request.home_country or composer.home_country
        session.commit()
        session.refresh(composer)
        new_data = ComposerModel.model_validate(composer)
        return UpdateComposerResponse(old_data=old_data, new_data=new_data, detail=f"Composer with ID: {composer_id} has been successfully updated.")

@app.put("/pieces/{piece_name}", tags=["pieces"], response_model=UpdatePieceResponse, status_code=status.HTTP_200_OK)
async def update_piece(piece_name: str, update_piece_request: UpdatePieceRequest) -> UpdatePieceResponse:
    with Session(bind=engine) as session:
        piece: PieceTable = session.execute(select(PieceTable).where(PieceTable.name == piece_name)).scalar_one_or_none()
        if not piece:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Piece name: '{piece_name}' not found.")
        if update_piece_request.composer_id is not None:
            if not session.execute(select(ComposerTable).where(update_piece_request.composer_id == ComposerTable.id)):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Composer ID: {update_piece_request.composer_id} not found.")
        old_data = PieceModel.model_validate(piece)
        piece.name = update_piece_request.name or piece.name
        piece.alt_name = update_piece_request.alt_name or piece.alt_name
        piece.difficulty = update_piece_request.difficulty or piece.difficulty
        piece.composer_id = update_piece_request.composer_id or piece.composer_id
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Difficulty is limited to the integers of 1 - 10 inclusively. Error: {error}")
        session.refresh(piece)
        new_data = PieceModel.model_validate(piece)
        return UpdatePieceResponse(old_data=old_data, new_data=new_data, detail=f"Piece with name: {piece_name} has been successfully updated.")

@app.delete("/composers/{composer_id}", tags=["composers"], response_model=DeleteComposerResponse, status_code=status.HTTP_200_OK)
async def delete_composer(composer_id: int) -> DeleteComposerResponse:
    with Session(bind=engine) as session:
        composer: ComposerTable = session.execute(select(ComposerTable).where(ComposerTable.id == composer_id)).scalar_one_or_none()
        if not composer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Composer ID: {composer_id} not found.")
        pieces: PieceTable = session.execute(select(PieceTable).where(PieceTable.composer_id == composer_id)).scalars().all()
        data = ComposerModel.model_validate(composer)
        for piece in pieces:
            session.delete(piece)
        session.delete(composer)
        session.commit()
        return DeleteComposerResponse(data=data, detail=f"Composer with composer ID: {composer_id} has successfully been deleted.")

@app.delete("/pieces/{piece_name}", tags=["pieces"], response_model=DeletePieceResponse, status_code=status.HTTP_200_OK)
async def delete_composer(piece_name: str) -> DeletePieceResponse:
    with Session(bind=engine) as session:
        piece: PieceTable = session.execute(select(PieceTable).where(PieceTable.name == piece_name)).scalar_one_or_none()
        if not piece:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Piece name: '{piece_name}' not found.")
        data = PieceModel.model_validate(piece)
        session.delete(piece)
        session.commit()
        return DeletePieceResponse(data=data, detail=f"Piece name: '{piece_name}' has successfully been deleted.")
