"""
Utility class for querying products and attributes.
"""

from sqlalchemy.orm import joinedload
from ..scoped_session import session_scope
from sqlalchemy.orm import Session 

from app.models import Product ,Attribute,AttributeValue 

from sqlalchemy.orm import joinedload
from pathlib import Path
import random 
import operator
from sqlalchemy import and_
from decimal import Decimal ,ROUND_UP

class ProductQuery:

    def __init__(self):
        self._get_session = session_scope

        src_dir = Path().cwd() /"app/static/assets/img"
        self.images = [str(i.relative_to(Path().cwd()/'app')) for i in src_dir.glob("*.jpg")]
  
    def _product_to_dict(self, product:Product):
        """
        Convert Product to dictionary with all relationships
        """
        
        return {
            "id": product.id,
            "name": product.name,
            "price":  Decimal(product.after_discount[0]).quantize(Decimal("0.01"), rounding=ROUND_UP),
            'category':product.category,
            'image_src':product.image_url or random.choice(self.images),
            'hiden_id':product.hiden_id,
            'discount':product.discount,
            'original_price':product.final_price.quantize(Decimal("0.01"), rounding=ROUND_UP),
            'description':product.description,
            'in_stock':product.stock,
            "attributes": {
                attr.name: [val.value for val in attr.values]
                for attr in product.attributes
            },
            "attribute_values": [
                {
                    "value": av.value,
                    "unit": av.unit,
                    "attribute_types": [a.name for a in av.attributes]
                }
                for av in product.attributes_values
            ]
        }

    def get_product(self, product_id):
        
        with self._get_session() as session:
            product = session.query(Product).options(
                joinedload(Product.attributes),
                joinedload(Product.attributes_values).joinedload(AttributeValue.attributes)
            ).filter_by(id=product_id).first()
            
            return self._product_to_dict(product) if product else None

    def get_products_by_attribute_value(self, attr_name, value, offset=0,limit=None):
      
        with self._get_session() as session:
            query = session.query(Product).options(
                joinedload(Product.attributes_values)
            ).join(
                Product.attributes_values
            ).join(
                AttributeValue.attributes
            ).filter(
                Attribute.name.ilike(attr_name),
                AttributeValue.value.ilike(value)
            )
            
            if limit:
                query = query.offset(offset).limit(limit)
                
            return [self._product_to_dict(p) for p in query.all()]


    @classmethod
    def generate_filter_query(cls,session:Session ,filters:dict[str]) ->Session:
        """_summary_

        Args:
            session (Session): _description_
            filters (dict[str]): _description_

        Returns:
            Session: _description_
        """
        query = session.query(Product).options(
            joinedload(Product.attributes_values)
        )
        
        for attr_name, values in filters.items():
            if attr_name.lower() == 'price_range':
                min_price, max_price = values
                query = query.filter(Product.price.between(min_price, max_price))
            else:
                query = query.join(
                    Product.attributes_values
                ).join(
                    AttributeValue.attributes
                ).filter(
                    Attribute.name.ilike(attr_name),
                    AttributeValue.value.in_(values)
                )
        return query 
    
    def filter_products(self, filters, limit=20 ,offset=0):
        """
        Filter products with multiple criteria, returning dictionaries
        """
        with self._get_session() as session:

            query = self.generate_filter_query(session ,filters)
            
            if limit:
                query = query.offset(offset).limit(limit)
            
            return [self._product_to_dict(p) for p in query.all()]

    def get_filter_options(self):
        """
        Get all available filter options as dictionary
        """
        with self._get_session() as session:
            attributes = session.query(Attribute).options(
                joinedload(Attribute.values)
            ).all()
            
            return {
                attr.name: [val.value for val in attr.values]
                for attr in attributes
            }
    
    def search(self ,query_term ,suggestion=False ,limit=20):
        with self._get_session() as session:
            products = session.query(Product).filter(
                Product.name.ilike(f'%{query_term}%')
            ).limit(limit).all()
            
            if suggestion:
                return [{'name':i.name,'category':i.category,'id':i.id} for i in products]
            
            results = [self._product_to_dict(p) for p in products]

            return results
    

    def search2(self, static_data: list[tuple],filters:dict={}, 
                offset=0,
                limit=None) -> list[dict]:

        if not static_data:
            raise ValueError("static_data cannot be empty")
        
        valid_operators = {'eq', 'ne', 'lt', 'le', 'gt', 'ge', 'like'}
        query_initiated = False
        with self._get_session() as query:

            if filters:
                query_initiated = True 
                query = self.generate_filter_query(session=query,
                                                  filters=filters)
                
            conditions = []
            for operator_name, field_name, value in static_data:
                if operator_name not in valid_operators:
                    raise ValueError(f"Invalid operator: {operator_name}")
                
                if not hasattr(Product, field_name):
                    raise ValueError(f"Invalid field: {field_name}")
                
                op = getattr(operator, operator_name)
                field = getattr(Product, field_name)
                conditions.append(op(field, value))
            
            if not query_initiated:
                query =query.query(Product) 

            products = query.filter(and_(*conditions)).offset(offset)

            if limit:
                products=products.limit(limit)
            
            return [self._product_to_dict(product) for product in products.all()]