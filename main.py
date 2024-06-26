from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session 
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

def get_db():
    with Session(bind=engine) as session:
        yield session

@app.get("/composers", tags=["composers"], response_model=GetComposersResponse, status_code=status.HTTP_200_OK)
async def get_composers(session: Session = Depends(get_db)) -> GetComposersResponse:
    composers: list[ComposerTable]= session.execute(select(ComposerTable)).scalars().all()
    composer_data_list = [ComposerModel.model_validate(composer) for composer in composers]
    return GetComposersResponse(data=composer_data_list, detail="Composers fetched successfully.")

@app.get("/pieces", tags=["pieces"], response_model=GetPiecesResponse, status_code=status.HTTP_200_OK)
async def get_pieces(composer_id: int | None = None, session: Session = Depends(get_db)) -> GetPiecesResponse:
    pieces: list[PieceTable] = session.execute(select(PieceTable)).scalars().all()
    piece_data_list = [PieceModel.model_validate(piece) for piece in pieces]
    if composer_id is not None:
        if not session.execute(select(ComposerTable).where(ComposerTable.id == composer_id)).scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Composer ID: {composer_id} not found.")
        piece_data_list = [piece for piece in piece_data_list if piece.composer_id == composer_id]
    return GetPiecesResponse(data=piece_data_list, detail="Pieces fetched successfully.")

@app.post("/composers", tags=["composers"], response_model=CreateComposerResponse, status_code=status.HTTP_201_CREATED)
async def add_composer(create_composer_request: CreateComposerRequest, session: Session = Depends(get_db)) -> CreateComposerResponse:
    new_composer: ComposerTable = ComposerTable(**create_composer_request.model_dump())
    session.add(new_composer)
    session.commit()
    session.refresh(new_composer)
    composer_data = ComposerModel.model_validate(new_composer)
    return CreateComposerResponse(data=composer_data, detail="Composer added successfully.")

@app.post("/pieces", tags=["pieces"], response_model=CreatePieceResponse, status_code=status.HTTP_201_CREATED)
async def add_piece(create_piece_request: CreatePieceRequest, session: Session = Depends(get_db)) -> PieceModel:
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

@app.put("/composers/{composer_id}", tags=["composers"], response_model=UpdateComposerResponse | CreatePieceResponse, status_code=status.HTTP_200_OK) 
async def update_composer(composer_id: int, update_composer_request: UpdateComposerRequest, session: Session = Depends(get_db)) -> UpdateComposerResponse | CreatePieceResponse:
    composer: ComposerTable = session.execute(select(ComposerTable).where(ComposerTable.id == composer_id)).scalar_one_or_none()
    if not composer:
        new_composer: ComposerTable = ComposerTable(**update_composer_request.model_dump())
        session.add(new_composer)
        session.commit()
        session.refresh(new_composer)
        composer_data = ComposerModel.model_validate(new_composer)
        return CreatePieceResponse(data=composer_data, detail="Composer added successfully.")
    old_data = ComposerModel.model_validate(composer)
    composer.name = update_composer_request.name or composer.name
    composer.home_country = update_composer_request.home_country or composer.home_country
    session.commit()
    session.refresh(composer)
    new_data = ComposerModel.model_validate(composer)
    return UpdateComposerResponse(old_data=old_data, new_data=new_data, detail=f"Composer with ID: {composer_id} has been successfully updated.")

@app.put("/pieces/{piece_name}", tags=["pieces"], response_model=UpdatePieceResponse | CreatePieceResponse, status_code=status.HTTP_200_OK)
async def update_piece(piece_name: str, update_piece_request: UpdatePieceRequest, session: Session = Depends(get_db)) -> UpdatePieceResponse | CreatePieceResponse:
    if update_piece_request.difficulty == 0 | update_piece_request.difficulty > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Difficulty is limited to the integers of 1 - 10 inclusively.")
    if update_piece_request.composer_id is not None:
        composer: ComposerTable = session.execute(select(ComposerTable).where(ComposerTable.id == update_piece_request.composer_id)).scalar_one_or_none()
        if not composer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Composer ID: {update_piece_request.composer_id} not found.")
    piece: PieceTable = session.execute(select(PieceTable).where(PieceTable.name == piece_name)).scalar_one_or_none()
    if not piece:
        new_piece: PieceTable = PieceTable(**update_piece_request.model_dump())
        session.add(new_piece)
        try:
            session.commit()
            return CreatePieceResponse(data=PieceModel.model_validate(new_piece), detail="Piece added successfully.")
        except IntegrityError as error:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Difficulty is limited to the integers of 1 - 10 inclusively. Error: {error}")
    old_data = PieceModel.model_validate(piece)
    for attr, value in update_piece_request.model_dump(exclude_unset=True).items():
        setattr(piece, attr, value)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Difficulty is limited to the integers of 1 - 10 inclusively.")
    session.refresh(piece)
    new_data = PieceModel.model_validate(piece)
    return UpdatePieceResponse(old_data=old_data, new_data=new_data, detail=f"Piece with name: {piece_name} has been successfully updated.")

@app.delete("/composers/{composer_id}", tags=["composers"], response_model=DeleteComposerResponse, status_code=status.HTTP_200_OK)
async def delete_composer(composer_id: int, session: Session = Depends(get_db)) -> DeleteComposerResponse:
    composer: ComposerTable = session.get(ComposerTable, composer_id)
    if not composer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Composer ID: {composer_id} not found.")
    data = ComposerModel.model_validate(composer)
    session.delete(composer)
    session.commit()
    return DeleteComposerResponse(data=data, detail=f"Composer with composer ID: {composer_id} has successfully been deleted.")

@app.delete("/pieces/{piece_name}", tags=["pieces"], response_model=DeletePieceResponse, status_code=status.HTTP_200_OK)
async def delete_composer(piece_name: str, session: Session = Depends(get_db)) -> DeletePieceResponse:
    piece: PieceTable = session.execute(select(PieceTable).where(PieceTable.name == piece_name)).scalar_one_or_none()
    if not piece:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Piece name: {piece_name} not found.")
    data = PieceModel.model_validate(piece)
    session.delete(piece)
    session.commit()
    return DeletePieceResponse(data=data, detail=f"Composer {piece_name} has successfully been deleted.")
