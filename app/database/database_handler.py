from sqlalchemy.orm import Session
from app.models.models import User, Artist, Event, Interest, SavedEvent
from app.schemas.schemas import (
    UserCreate, UserUpdate,
    ArtistCreate, ArtistUpdate,
    EventCreate, EventUpdate,
    InterestCreate, InterestUpdate,
    SavedEventCreate, SavedEventUpdate
)
import uuid
from uuid import UUID
from datetime import datetime
from app.auth import hash_password


# ----- User CRUD -----

def create_user(db: Session, user_data: UserCreate):
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        id=uuid.uuid4(),
        name=user_data.name,
        email=user_data.email,
        password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: UUID, user_in: UserUpdate):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    data = user_in.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(user, field, val)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: UUID):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user


# ----- Artist CRUD -----

def create_artist(db: Session, artist_in: ArtistCreate):
    new_artist = Artist(id=uuid.uuid4(), **artist_in.model_dump())
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)
    return new_artist

def get_artists(db: Session):
    return db.query(Artist).all()

def get_artist_by_id(db: Session, artist_id: UUID):
    return db.query(Artist).filter(Artist.id == artist_id).first()

def update_artist(db: Session, artist_id: UUID, artist_in: ArtistUpdate):
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        return None
    data = artist_in.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(artist, field, val)
    db.commit()
    db.refresh(artist)
    return artist

def delete_artist(db: Session, artist_id: UUID):
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        return None
    db.delete(artist)
    db.commit()
    return artist


# ----- Event CRUD -----

def create_event(db: Session, event_in: EventCreate):
    new_event = Event(id=uuid.uuid4(), **event_in.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def get_events(db: Session):
    return db.query(Event).all()

def get_event_by_id(db: Session, event_id: UUID):
    return db.query(Event).filter(Event.id == event_id).first()

def update_event(db: Session, event_id: UUID, event_in: EventUpdate):
    event = get_event_by_id(db, event_id)
    if not event:
        return None
    data = event_in.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(event, field, val)
    db.commit()
    db.refresh(event)
    return event

def delete_event(db: Session, event_id: UUID):
    event = get_event_by_id(db, event_id)
    if not event:
        return None
    db.delete(event)
    db.commit()
    return event


# ----- Interest CRUD -----

def create_interest(db: Session, interest_in: InterestCreate):
    existing = db.query(Interest).filter_by(
        user_id=interest_in.user_id,
        artist_id=interest_in.artist_id
    ).first()
    if existing:
        return existing
    new_interest = Interest(id=uuid.uuid4(), **interest_in.model_dump())
    db.add(new_interest)
    db.commit()
    db.refresh(new_interest)
    return new_interest

def get_interests(db: Session):
    return db.query(Interest).all()

def get_interests_for_user(db: Session, user_id: UUID):
    return db.query(Interest).filter(Interest.user_id == user_id).all()

def get_interest_by_id(db: Session, interest_id: UUID):
    return db.query(Interest).filter(Interest.id == interest_id).first()

def update_interest(db: Session, interest_id: UUID, interest_in: InterestUpdate):
    interest = get_interest_by_id(db, interest_id)
    if not interest:
        return None
    data = interest_in.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(interest, field, val)
    db.commit()
    db.refresh(interest)
    return interest

def delete_interest(db: Session, interest_id: UUID):
    interest = get_interest_by_id(db, interest_id)
    if not interest:
        return None
    db.delete(interest)
    db.commit()
    return interest


# ----- SavedEvent CRUD -----

def create_saved_event(db: Session, saved_in: SavedEventCreate):
    existing = db.query(SavedEvent).filter_by(
        user_id=saved_in.user_id,
        event_id=saved_in.event_id
    ).first()
    if existing:
        return existing
    new_saved = SavedEvent(id=uuid.uuid4(), **saved_in.model_dump())
    db.add(new_saved)
    db.commit()
    db.refresh(new_saved)
    return new_saved

def get_saved_events(db: Session):
    return db.query(SavedEvent).all()

def get_saved_events_for_user(db: Session, user_id: UUID):
    return db.query(SavedEvent).filter(SavedEvent.user_id == user_id).all()

def get_saved_event_by_id(db: Session, se_id: UUID):
    return db.query(SavedEvent).filter(SavedEvent.id == se_id).first()

def update_saved_event(db: Session, se_id: UUID, se_in: SavedEventUpdate):
    se = get_saved_event_by_id(db, se_id)
    if not se:
        return None
    data = se_in.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(se, field, val)
    db.commit()
    db.refresh(se)
    return se

def delete_saved_event(db: Session, se_id: UUID):
    se = get_saved_event_by_id(db, se_id)
    if not se:
        return None
    db.delete(se)
    db.commit()
    return se


# ----- Discovery helpers -----

def get_or_create_artist_by_ticketmaster_data(db: Session, artist_data: dict):
    ticketmaster_id = artist_data.get("id")
    name = artist_data.get("name")
    if not ticketmaster_id or not name:
        return None
    existing = db.query(Artist).filter_by(ticketmaster_id=ticketmaster_id).first()
    if existing:
        return existing
    new_artist = Artist(id=uuid.uuid4(), name=name, ticketmaster_id=ticketmaster_id)
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)
    return new_artist

def get_or_create_event_by_ticketmaster_data(db: Session, artist_id: UUID, event_data: dict):
    tm_id = event_data.get("id")
    if not tm_id:
        return None
    existing = db.query(Event).filter_by(ticketmaster_id=tm_id).first()
    if existing:
        return existing
    date_str = event_data.get("date")
    event_datetime = None
    if date_str:
        event_datetime = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    new_event = Event(
        id=uuid.uuid4(),
        ticketmaster_id=tm_id,
        artist_id=artist_id,
        name=event_data.get("name"),
        date=event_datetime,
        location=event_data.get("location"),
        ticket_url=event_data.get("ticket_url"),
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def get_events_for_artist(db: Session, artist_id: UUID):
    return db.query(Event).filter(Event.artist_id == artist_id).all()
