from sqlalchemy import Column, String, UUID, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Artist(Base):
    __tablename__ = "artists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    ticketmaster_id = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now(), server_default=func.now())

    events = relationship("Event", back_populates="artist")
    interests = relationship("Interest", back_populates="artist")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticketmaster_id = Column(String, nullable=True)
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id", ondelete="CASCADE"))
    name = Column(String(200), nullable=False)
    date = Column(TIMESTAMP, nullable=True)
    location = Column(String(200), nullable=True)
    ticket_url = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now(), server_default=func.now())

    artist = relationship("Artist", back_populates="events")
    saved_events = relationship("SavedEvent", back_populates="event")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    location = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now(), server_default=func.now())

    interests = relationship("Interest", back_populates="user")
    saved_events = relationship("SavedEvent", back_populates="user")


class Interest(Base):
    __tablename__ = "interests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, nullable=False, default=func.now(), server_default=func.now())

    user = relationship("User", back_populates="interests")
    artist = relationship("Artist", back_populates="interests")


class SavedEvent(Base):
    __tablename__ = "saved_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, nullable=False, default=func.now(), server_default=func.now())

    user = relationship("User", back_populates="saved_events")
    event = relationship("Event", back_populates="saved_events")
