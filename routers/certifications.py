from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, security

router = APIRouter(prefix="/api/v1/certifications", tags=["certifications"])

@router.post("/", response_model=schemas.CertificationOut, status_code=status.HTTP_201_CREATED)
def create_certification(
    payload: schemas.CertificationCreate,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    cert = models.Certification(
        caterer_id=current_caterer.id,
        title=payload.title,
        issued_by=payload.issued_by,
        issue_date=payload.issue_date,
        certificate_url=payload.certificate_url
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.get("/", response_model=List[schemas.CertificationOut])
def get_certifications(
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
        
    return db.query(models.Certification).filter(models.Certification.caterer_id == target_caterer_id).all()


@router.put("/{id}", response_model=schemas.CertificationOut)
def update_certification(
    id: int,
    payload: schemas.CertificationCreate,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    cert = db.query(models.Certification).filter(
        models.Certification.id == id,
        models.Certification.caterer_id == current_caterer.id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    cert.title = payload.title
    cert.issued_by = payload.issued_by
    cert.issue_date = payload.issue_date
    cert.certificate_url = payload.certificate_url
    
    db.commit()
    db.refresh(cert)
    return cert


@router.delete("/{id}", response_model=schemas.MessageResponse)
def delete_certification(
    id: int,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    cert = db.query(models.Certification).filter(
        models.Certification.id == id,
        models.Certification.caterer_id == current_caterer.id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    db.delete(cert)
    db.commit()
    return {"message": "Certification deleted successfully"}
