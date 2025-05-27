from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.models import User
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

router = APIRouter(prefix="/saved_events", tags=["saved_events"])

@router.post("/", response_model=SavedEventResponse)
def create_saved_event_route(
    saved_event_in: SavedEventCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # link saved event to me
    saved_event_in.user_id = _current_user.id
    return create_saved_event(db, saved_event_in)

@router.get("/", response_model=list[SavedEventResponse])
def list_saved_events_route(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # list only my saved events
    return get_saved_events_for_user(db, _current_user.id)

@router.get("/{saved_event_id}", response_model=SavedEventResponse)
def read_saved_event(
    saved_event_id: UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # get one saved event by me
    se = get_saved_event_by_id(db, saved_event_id)
    if not se or se.user_id != _current_user.id:
        raise HTTPException(status_code=404, detail="SavedEvent not found")
    return se

@router.patch("/{saved_event_id}", response_model=SavedEventResponse)
def update_saved_event_route(
    saved_event_id: UUID,
    se_in: SavedEventUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # update only my saved event
    se = get_saved_event_by_id(db, saved_event_id)
    if not se or se.user_id != _current_user.id:
        raise HTTPException(status_code=404, detail="SavedEvent not found")
    return update_saved_event(db, saved_event_id, se_in)

@router.delete("/{saved_event_id}", response_model=SavedEventResponse)
def delete_saved_event_route(
    saved_event_id: UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # delete only my saved event
    se = get_saved_event_by_id(db, saved_event_id)
    if not se or se.user_id != _current_user.id:
        raise HTTPException(status_code=404, detail="SavedEvent not found")
    return delete_saved_event(db, saved_event_id)
