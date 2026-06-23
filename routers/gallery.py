import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, security

router = APIRouter(prefix="/api/v1/gallery", tags=["gallery"])

@router.post("/upload", response_model=schemas.GalleryItemOut, status_code=status.HTTP_201_CREATED)
def upload_gallery_item(
    payload: schemas.GalleryItemCreate,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    item = models.GalleryItem(
        caterer_id=current_caterer.id,
        type=payload.type,
        file_url=payload.file_url
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=List[schemas.GalleryItemOut])
def get_gallery(
    caterer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(security.oauth2_scheme)
):
    target_caterer_id = caterer_id
    if target_caterer_id is None and token:
        try:
            payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
            caterer_id_str = payload.get("sub")
            if caterer_id_str:
                target_caterer_id = int(caterer_id_str)
        except Exception:
            pass

    if target_caterer_id is None:
        raise HTTPException(status_code=400, detail="caterer_id is required or authenticate as a vendor.")

    return db.query(models.GalleryItem).filter(models.GalleryItem.caterer_id == target_caterer_id).all()


@router.delete("/{id}", response_model=schemas.MessageResponse)
def delete_gallery_item(
    id: int,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    item = db.query(models.GalleryItem).filter(
        models.GalleryItem.id == id,
        models.GalleryItem.caterer_id == current_caterer.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    db.delete(item)
    db.commit()
    return {"message": "Gallery item deleted successfully"}
