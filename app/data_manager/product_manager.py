from sqlalchemy.orm import joinedload
from .scoped_session import session_scope
from app.models import Product ,Attribute,AttributeValue 

from sqlalchemy.orm import joinedload
from pathlib import Path
import random 


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
            "price": product.price,
            'category':product.category,
            'image_src':product.image_url or random.choice(self.images),
            'original_price':product.price +100,
            'discount':100,
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

    def filter_products(self, filters, limit=20 ,offset=0):
        """
        Filter products with multiple criteria, returning dictionaries
        """
        with self._get_session() as session:
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