from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.schemas import InterestCreate, InterestResponse, InterestUpdate
from app.database.database_handler import (
    create_interest,
    get_interests_for_user,
    get_interest_by_id,
    update_interest,
    delete_interest,
)
from app.database.database import get_db
from app.main import get_current_user, get_current_admin

router = APIRouter(
    prefix="/interests",
    tags=["interests"],
)

@router.get("/", response_model=list[InterestResponse], dependencies=[Depends(get_current_user)])
def list_interests_route(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_interests_for_user(db, current_user.id)

@router.post("/{user_id}/{artist_id}", response_model=InterestResponse,
             dependencies=[Depends(get_current_admin)])
def admin_create_interest_route(
    user_id: UUID,
    artist_id: UUID,
    db: Session = Depends(get_db),
):
    return create_interest(db, user_id, artist_id)

@router.patch("/{interest_id}", response_model=InterestResponse,
            dependencies=[Depends(get_current_user)])
def update_interest_route(
    interest_id: UUID,
    interest_in: InterestUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    interest = get_interest_by_id(db, interest_id)
    if not interest or interest.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")
    return update_interest(db, interest_id, interest_in)

@router.delete("/{interest_id}", response_model=InterestResponse,
               dependencies=[Depends(get_current_user)])
def delete_interest_route(
    interest_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    interest = get_interest_by_id(db, interest_id)
    if not interest or interest.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")
    return delete_interest(db, interest_id)
