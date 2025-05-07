
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base ,product_attribute_link,attribute_value_link ,product_attribute_values

class Attribute(Base):
    __tablename__ = 'attributes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # "color", "size", etc.
    data_type = Column(String)  # "string", "number", "size_range"
    
    # Relationships
    products = relationship(
        "Product", 
        secondary=product_attribute_link,
        back_populates="attributes",
        lazy='dynamic'
    )
    values = relationship(
        "AttributeValue",
        secondary=attribute_value_link,
        back_populates="attributes"
    )
    def __repr__(self):
        return f"<Attribute(id={self.id}, name='{self.name}', data_type='{self.data_type}')>"


class AttributeValue(Base):
    __tablename__ = 'attribute_values'
    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)  # "red", "39-42", "XL"
    unit = Column(String)  # "mm", "inches", "EU" (optional)
    
    # Relationships
    attributes = relationship(
        "Attribute", 
        secondary=attribute_value_link,
        back_populates="values"
    )
    products = relationship(
        'Product',
        secondary=product_attribute_values,
        back_populates='attributes_values',lazy='dynamic'
    )
    def __repr__(self):
        if self.unit:
            return f"<AttributeValue(id={self.id}, value='{self.value}', unit='{self.unit}')>"
        return f"<AttributeValue(id={self.id}, value='{self.value}')>"

