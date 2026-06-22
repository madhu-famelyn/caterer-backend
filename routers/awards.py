from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, security

router = APIRouter(prefix="/api/v1/awards", tags=["awards"])

@router.post("/", response_model=schemas.AwardOut, status_code=status.HTTP_201_CREATED)
def create_award(
    payload: schemas.AwardCreate,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    award = models.Award(
        caterer_id=current_caterer.id,
        title=payload.title,
        year=payload.year,
        image_url=payload.image_url,
        description=payload.description
    )
    db.add(award)
    db.commit()
    db.refresh(award)
    return award


@router.get("/", response_model=List[schemas.AwardOut])
def get_awards(
    caterer_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(security.oauth2_scheme)
):
    target_caterer_id = caterer_id
    if target_caterer_id is None and token:
        try:
            payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
            caterer_id_str = payload.get("sub")
            if caterer_id_str:
                target_caterer_id = int(caterer_id_str)
        except Exception:
            pass
            
    if target_caterer_id is None:
        raise HTTPException(status_code=400, detail="caterer_id is required or authenticate as a vendor.")
        
    return db.query(models.Award).filter(models.Award.caterer_id == target_caterer_id).all()


@router.put("/{id}", response_model=schemas.AwardOut)
def update_award(
    id: int,
    payload: schemas.AwardCreate,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    award = db.query(models.Award).filter(
        models.Award.id == id,
        models.Award.caterer_id == current_caterer.id
    ).first()
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")
    
    award.title = payload.title
    award.year = payload.year
    award.image_url = payload.image_url
    award.description = payload.description
    
    db.commit()
    db.refresh(award)
    return award


@router.delete("/{id}", response_model=schemas.MessageResponse)
def delete_award(
    id: int,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    award = db.query(models.Award).filter(
        models.Award.id == id,
        models.Award.caterer_id == current_caterer.id
    ).first()
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")
    db.delete(award)
    db.commit()
    return {"message": "Award deleted successfully"}
