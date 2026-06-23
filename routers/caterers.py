from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas, security
from database import get_db

router = APIRouter(prefix="/api/v1/caterers", tags=["caterers"])


def caterer_to_out(caterer: models.Caterer) -> schemas.CatererOut:
    """Convert DB model → CatererOut (parse comma-separated tags)."""
    tags = [t.strip() for t in (caterer.service_tags or "").split(",") if t.strip()]
    data = {
        "id": caterer.id,
        "business_name": caterer.business_name,
        "owner_name": caterer.owner_name,
        "email": caterer.email,
        "mobile": caterer.mobile,
        "address": caterer.address,
        "city": caterer.city,
        "state": caterer.state,
        "zip": caterer.zip,
        "cuisine_type": caterer.cuisine_type,
        "bio": caterer.bio,
        "price_per_guest": caterer.price_per_guest,
        "tags": tags,
        "image_url": caterer.image_url,
        "rating": caterer.rating,
        "review_count": caterer.review_count,
        "verified": caterer.verified,
        "created_at": caterer.created_at,
    }
    return schemas.CatererOut(**data)


# ── Register (POST /) ─────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.CatererOut, status_code=status.HTTP_201_CREATED)
def register_caterer(payload: schemas.CatererCreate, db: Session = Depends(get_db)):
    # Check duplicate email
    existing = db.query(models.Caterer).filter(models.Caterer.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    tags_str = ",".join(payload.service_tags or [])

    caterer = models.Caterer(
        business_name=payload.business_name,
        owner_name=payload.owner_name,
        email=payload.email,
        mobile=payload.mobile,
        hashed_password=security.hash_password(payload.password),
        address=payload.address,
        city=payload.city,
        state=payload.state,
        zip=payload.zip,
        cuisine_type=payload.cuisine_type,
        bio=payload.bio,
        price_per_guest=payload.price_per_guest,
        service_tags=tags_str,
        image_url=payload.image_url,
        verified=False,
        rating=0.0,
        review_count=0,
    )
    db.add(caterer)
    db.commit()
    db.refresh(caterer)
    return caterer_to_out(caterer)


# ── Bulk Register (POST /bulk) ───────────────────────────────────────────────

@router.post("/bulk", response_model=schemas.BulkUploadResponse, status_code=status.HTTP_201_CREATED)
def bulk_register_caterers(payload: List[schemas.CatererCreate], db: Session = Depends(get_db)):
    created = []
    errors = []

    for item in payload:
        # Check duplicate email
        existing = db.query(models.Caterer).filter(models.Caterer.email == item.email).first()
        if existing:
            errors.append({"email": item.email, "error": "Email already registered"})
            continue

        try:
            tags_str = ",".join(item.service_tags or [])
            caterer = models.Caterer(
                business_name=item.business_name,
                owner_name=item.owner_name,
                email=item.email,
                mobile=item.mobile,
                hashed_password=security.hash_password(item.password),
                address=item.address,
                city=item.city,
                state=item.state,
                zip=item.zip,
                cuisine_type=item.cuisine_type,
                bio=item.bio,
                price_per_guest=item.price_per_guest,
                service_tags=tags_str,
                image_url=item.image_url,
                verified=False,
                rating=0.0,
                review_count=0,
            )
            db.add(caterer)
            db.commit()
            db.refresh(caterer)
            created.append(caterer_to_out(caterer))
        except Exception as e:
            db.rollback()
            errors.append({"email": item.email, "error": str(e)})

    return {
        "created_count": len(created),
        "failed_count": len(errors),
        "created": created,
        "errors": errors
    }


# ── List (GET /) ──────────────────────────────────────────────────────────────

@router.get("/", response_model=List[schemas.CatererOut])
def list_caterers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    city: Optional[str] = Query(None),
    cuisine_type: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Caterer)

    if city:
        query = query.filter(models.Caterer.city.ilike(f"%{city}%"))
    if cuisine_type:
        query = query.filter(models.Caterer.cuisine_type.ilike(f"%{cuisine_type}%"))
    if q:
        query = query.filter(
            models.Caterer.business_name.ilike(f"%{q}%") |
            models.Caterer.city.ilike(f"%{q}%") |
            models.Caterer.cuisine_type.ilike(f"%{q}%")
        )

    caterers = query.order_by(models.Caterer.rating.desc()).offset(skip).limit(limit).all()
    return [caterer_to_out(c) for c in caterers]


# ── Get one (GET /{id}) ────────────────────────────────────────────────────────

@router.get("/{caterer_id}", response_model=schemas.CatererOut)
def get_caterer(caterer_id: int, db: Session = Depends(get_db)):
    caterer = db.query(models.Caterer).filter(models.Caterer.id == caterer_id).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")
    return caterer_to_out(caterer)


# ── Update (PUT /{id}) ────────────────────────────────────────────────────────

@router.put("/{caterer_id}", response_model=schemas.CatererOut)
def update_caterer(
    caterer_id: int,
    payload: schemas.CatererUpdate,
    db: Session = Depends(get_db),
):
    caterer = db.query(models.Caterer).filter(models.Caterer.id == caterer_id).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "service_tags" in update_data:
        update_data["service_tags"] = ",".join(update_data.pop("service_tags") or [])

    for key, value in update_data.items():
        setattr(caterer, key, value)

    db.commit()
    db.refresh(caterer)
    return caterer_to_out(caterer)


# ── Delete (DELETE /{id}) ─────────────────────────────────────────────────────

@router.delete("/{caterer_id}", response_model=schemas.MessageResponse)
def delete_caterer(caterer_id: int, db: Session = Depends(get_db)):
    caterer = db.query(models.Caterer).filter(models.Caterer.id == caterer_id).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")
    db.delete(caterer)
    db.commit()
    return {"message": "Caterer deleted successfully"}
