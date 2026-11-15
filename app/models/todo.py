from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone

class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index = True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    deadline = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    past_deadline = Column(Boolean, default=False)