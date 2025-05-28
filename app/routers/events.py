from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.schemas import EventCreate, EventResponse, EventUpdate
from app.database.database_handler import (
    create_event,
    get_events,
    get_event_by_id,
    update_event,
    delete_event,
)
from app.database.database import get_db
from app.main import get_current_user, get_current_admin

router = APIRouter(
    prefix="/events",
    tags=["events"],
)

@router.get("/", response_model=list[EventResponse], dependencies=[Depends(get_current_user)])
def list_events_route(
    db: Session = Depends(get_db),
):
    return get_events(db)

@router.get("/{event_id}", response_model=EventResponse, dependencies=[Depends(get_current_user)])
def read_event_route(
    event_id: UUID,
    db: Session = Depends(get_db),
):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_admin)])
def create_event_route(
    event_in: EventCreate,
    db: Session = Depends(get_db),
):
    return create_event(db, event_in)

@router.patch("/{event_id}", response_model=EventResponse,
            dependencies=[Depends(get_current_admin)])
def update_event_route(
    event_id: UUID,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
):
    updated = update_event(db, event_id, event_in)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return updated

@router.delete("/{event_id}", response_model=EventResponse,
               dependencies=[Depends(get_current_admin)])
def delete_event_route(
    event_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = delete_event(db, event_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return deleted
