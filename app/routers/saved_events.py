from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.schemas import SavedEventCreate, SavedEventResponse, SavedEventUpdate
from app.database.database_handler import (
    create_saved_event,
    get_saved_events_for_user,
    get_saved_event_by_id,
    update_saved_event,
    delete_saved_event,
)
from app.database.database import get_db
from app.main import get_current_user

router = APIRouter(
    prefix="/saved_events",
    tags=["saved_events"],
)

@router.get("/", response_model=list[SavedEventResponse], dependencies=[Depends(get_current_user)])
def list_saved_events_route(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_saved_events_for_user(db, current_user.id)

@router.post("/{event_id}", response_model=SavedEventResponse,
             dependencies=[Depends(get_current_user)])
def create_saved_event_route(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    saved_in = SavedEventCreate(user_id=current_user.id, event_id=event_id)
    return create_saved_event(db, saved_in)

@router.patch("/{saved_event_id}", response_model=SavedEventResponse,
            dependencies=[Depends(get_current_user)])
def update_saved_event_route(
    saved_event_id: UUID,
    se_in: SavedEventUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    se = get_saved_event_by_id(db, saved_event_id)
    if not se or se.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SavedEvent not found")
    return update_saved_event(db, saved_event_id, se_in)

@router.delete("/{saved_event_id}", response_model=SavedEventResponse,
               dependencies=[Depends(get_current_user)])
def delete_saved_event_route(
    saved_event_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    se = get_saved_event_by_id(db, saved_event_id)
    if not se or se.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SavedEvent not found")
    return delete_saved_event(db, saved_event_id)
