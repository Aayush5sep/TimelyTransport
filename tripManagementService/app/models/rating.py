import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, func
from sqlalchemy.orm import Session

from app.database import Base
from app.schemas.rating import RatingCreate


class Rating(Base):
    __tablename__ = "rating"

    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    customer_id = Column(String(36), nullable=False)
    driver_id = Column(String(36), nullable=False)
    trip_id = Column(String(36), ForeignKey("booking.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    feedback = Column(String(255), nullable=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.id or str(uuid.uuid4())
    
    @classmethod
    def create_rating(cls, db: Session, rating_data: RatingCreate):
        """
        Create a new rating and store it in the database.
        """
        new_rating = cls(**rating_data.model_dump())
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating
    
    @classmethod
    def get_rating_by_trip_id(cls, db: Session, trip_id: str):
        """
        Fetch the rating for a specific trip.
        """
        return db.query(cls).filter(cls.trip_id == trip_id).first()

    @classmethod
    def get_driver_ratings(cls, db: Session, driver_id: str):
        """
        Fetch all ratings and calculate the average rating for the driver.
        """
        ratings = db.query(cls).filter(cls.driver_id == driver_id).all()

        # Calculate average rating (if no ratings, return 0)
        avg_rating = db.query(func.avg(cls.rating)).filter(cls.driver_id == driver_id).scalar() or 0

        return {
            "driver_id": driver_id,
            "average_rating": round(avg_rating, 2),
            "ratings": ratings
        }