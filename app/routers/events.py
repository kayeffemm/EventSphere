from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.models import User
from app.schemas.schemas import EventCreate, EventResponse, EventUpdate
from app.database.database_handler import (
    create_event,
    get_events,
    get_event_by_id,
    update_event,
    delete_event,
)
from app.database.database import get_db
from app.main import get_current_user

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse)
def create_event_route(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # add a new event
    return create_event(db, event_in)

@router.get("/", response_model=list[EventResponse])
def list_events_route(db: Session = Depends(get_db)):
    # list all events
    return get_events(db)

@router.get("/{event_id}", response_model=EventResponse)
def read_event(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    # get one event
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.patch("/{event_id}", response_model=EventResponse)
def update_event_route(
    event_id: UUID,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # update event data
    updated = update_event(db, event_id, event_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated

@router.delete("/{event_id}", response_model=EventResponse)
def delete_event_route(
    event_id: UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # remove an event
    deleted = delete_event(db, event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return deleted
