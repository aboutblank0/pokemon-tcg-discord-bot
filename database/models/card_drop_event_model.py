from sqlalchemy import ARRAY, BigInteger, Column, DateTime, ForeignKey, String, func
from database.models.base import Base

class CardDropEventModel(Base):
    __tablename__ = "card_drop_events"
    
    created_at = Column(DateTime, default=func.now())

    id = Column(String, primary_key=True, unique=True)
    cards_dropped_ids = Column(ARRAY(String), nullable=False)
    started_by_user_id = Column(BigInteger, ForeignKey("users.discord_user_id"), nullable=False)
