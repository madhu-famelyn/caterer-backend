from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas, security

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])

@router.post("/", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: schemas.ReviewCreate,
    db: Session = Depends(get_db)
):
    caterer = db.query(models.Caterer).filter(models.Caterer.id == payload.caterer_id).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")

    review = models.Review(
        caterer_id=payload.caterer_id,
        customer_name=payload.customer_name,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # Recalculate rating and review count
    reviews_stats = db.query(
        models.Review.rating
    ).filter(models.Review.caterer_id == payload.caterer_id).all()
    
    if reviews_stats:
        ratings = [r[0] for r in reviews_stats]
        caterer.review_count = len(ratings)
        caterer.rating = round(sum(ratings) / len(ratings), 1)
        db.commit()
        
    return review


@router.get("/", response_model=List[schemas.ReviewOut])
def get_reviews(
    caterer_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.Review).filter(models.Review.caterer_id == caterer_id).order_by(models.Review.created_at.desc()).all()


@router.delete("/{id}", response_model=schemas.MessageResponse)
def delete_review(
    id: int,
    db: Session = Depends(get_db),
    current_caterer: models.Caterer = Depends(security.get_current_caterer)
):
    review = db.query(models.Review).filter(
        models.Review.id == id,
        models.Review.caterer_id == current_caterer.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found on your profile")
    
    db.delete(review)
    db.commit()
    
    # Recalculate average rating and review count
    reviews_stats = db.query(
        models.Review.rating
    ).filter(models.Review.caterer_id == current_caterer.id).all()
    
    caterer = db.query(models.Caterer).filter(models.Caterer.id == current_caterer.id).first()
    if reviews_stats:
        ratings = [r[0] for r in reviews_stats]
        caterer.review_count = len(ratings)
        caterer.rating = round(sum(ratings) / len(ratings), 1)
    else:
        caterer.review_count = 0
        caterer.rating = 0.0
    db.commit()
    
    return {"message": "Review deleted successfully"}
