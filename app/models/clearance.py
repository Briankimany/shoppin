

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .utils import Base , clearance_user_association


class ClearanceLevel(Base):
    __tablename__ = 'clearance_levels'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    level = Column(Integer, nullable=False, unique=True)

    users = relationship("UserProfile" ,secondary=clearance_user_association ,back_populates='clearance')

    def __repr__(self):
        return f"<ClearanceLevel {self.level}: {self.name}>"
