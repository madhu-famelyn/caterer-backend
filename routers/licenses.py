from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, security

router = APIRouter(prefix="/api/v1/licenses", tags=["licenses"])

@router.post("/", response_model=schemas.LicenseOut, status_code=status.HTTP_201_CREATED)
def create_license(
    payload: schemas.LicenseCreate,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    license_item = models.License(
        caterer_id=current_caterer.id,
        title=payload.title,
        description=payload.description,
        document_url=payload.document_url,
        expiry_date=payload.expiry_date
    )
    db.add(license_item)
    db.commit()
    db.refresh(license_item)
    return license_item


@router.get("/", response_model=List[schemas.LicenseOut])
def get_licenses(
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
        
    return db.query(models.License).filter(models.License.caterer_id == target_caterer_id).all()


@router.put("/{id}", response_model=schemas.LicenseOut)
def update_license(
    id: int,
    payload: schemas.LicenseCreate,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    license_item = db.query(models.License).filter(
        models.License.id == id,
        models.License.caterer_id == current_caterer.id
    ).first()
    if not license_item:
        raise HTTPException(status_code=404, detail="License not found")
    
    license_item.title = payload.title
    license_item.description = payload.description
    license_item.document_url = payload.document_url
    license_item.expiry_date = payload.expiry_date
    
    db.commit()
    db.refresh(license_item)
    return license_item


@router.delete("/{id}", response_model=schemas.MessageResponse)
def delete_license(
    id: int,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    license_item = db.query(models.License).filter(
        models.License.id == id,
        models.License.caterer_id == current_caterer.id
    ).first()
    if not license_item:
        raise HTTPException(status_code=404, detail="License not found")
    db.delete(license_item)
    db.commit()
    return {"message": "License deleted successfully"}
