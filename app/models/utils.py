
from sqlalchemy.orm import relationship
from sqlalchemy import Table ,ForeignKey ,Column,Integer
from .base import Base

clearance_user_association = Table(
    'user_clearance',
    Base.metadata,
    Column("user_id",Integer , ForeignKey("user_table.id")),
    Column("clearance_id",Integer , ForeignKey("clearance_levels.id"))

) 