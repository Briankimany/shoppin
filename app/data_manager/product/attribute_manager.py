"""
Utility class to manage products and their attributes.
"""
from app.models.product_details import Attribute, AttributeValue
from app.models.product import Product ,Vendor
from app.data_manager.scoped_session import session_scope
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.data_manager.charges_manager import ChargeRuleManager ,Payee

class ProductManager:
    """
    Manages the creation and updating of products, including their attributes and values.
    """

    session_scope = staticmethod(session_scope)
    @classmethod
    def create_charge_product(cls,product_data:Dict) ->int:
        """ creates a product with charges.

        Args:
            product_data (Dict[str, Any]): Dictionary containing product details.
                Required keys: name, description, price, stock, category, image_url, preview_url, product_type,vendor_id
                Optional keys: vendor_commission
                vendor_id (int): The ID of the vendor who owns the product.
                vendor_commission (float): The percentage of the commission to be paid by the vendor.
        Returns:
            int: The ID of the created product.
        Raises:
            Exception: If there's an error during product creation.
        """

        commission_from_vendor = product_data.get('vendor_commission',0)
        if commission_from_vendor:
            product_data.pop('vendor_commission')
        
        with cls.session_scope(func=cls.create_charge_product) as db_session:

            vendor = db_session.query(Vendor).filter_by(id=product_data['vendor_id']).first()
            if not vendor:
                raise Exception(f"Vendor with ID {product_data['vendor_id']} not found")
            
            product = cls.create_product(
                db_session=db_session,
                product_data=product_data
            )
            cls.add_charges(
                vendor=vendor,
                commision_from_vendor=commission_from_vendor,
                product=product,
                db_session=db_session
            )
            db_session.commit()

            return product.id 

    @classmethod
    def add_charges(cls,vendor:Vendor,commision_from_vendor:float,product:Product,
                     db_session:Session) :
        """Add charges to a product. 

        Args:
            vendor (Vendor): The vendor who owns the product.
            commision_from_vendor (float): The percentage of the commission to be paid by the vendor.
            product (Product): The product to which charges will be added.
            db_session (Session): The database session.

        Returns:
            None
        """
        if commision_from_vendor:
            ChargeRuleManager.create_product_charge_rule(
                        db_session=db_session,
                        product_id=product.id,
                        percentage=commision_from_vendor,
                        payee=Payee('vendor',vendor.id)
                        )
    
        ChargeRuleManager.create_product_charge_rule(
            db_session=db_session,
            product_id=product.id,
            percentage=100-commision_from_vendor,
            payee=Payee('product',product.id)
        )

    @classmethod
    def create_product(cls, db_session:Session,product_data: Dict[str, Any]) -> Product:
        """
        Creates a new product with the given data.

        Args:
            product_data (Dict[str, Any]): Dictionary containing product details.
                Required keys: name, description, price, stock, category, image_url, preview_url, product_type
           
        Returns:
            Product: The newly created product instance.

        Raises:
            Exception: If there's an error during product creation.
        """
        product = db_session.query(Product).filter(Product.name == product_data['name']).first()
        if product:
            return product
        
        product = Product(**product_data)
        db_session.add(product)
        db_session.commit()
        return product
    
    @classmethod
    def update_product_attributes(cls, product_id: int, attribute_data: Dict[str, List[str]]) -> None:
        """
        Updates or adds attributes and their values to an existing product.

        Args:
            product_id (int): The ID of the product to update.
            attribute_data (Dict[str, List[str]]): Dictionary of attributes and their values.
                Format: {attribute_name: [value1, value2, ...], ...}

        Raises:
            Exception: If there's an error during attribute update.
        """
        with cls.session_scope(func=cls.update_product_attributes
                               ) as db_session:
            
            try:
                product = db_session.query(Product).filter_by(id=product_id).first()
                if not product:
                    raise Exception(f"Product with ID {product_id} not found")

                for attr_name, values in attribute_data.items():
                    attribute = db_session.query(Attribute).filter_by(name=attr_name).first()
                    if not attribute:
                        attribute = Attribute(name=attr_name, data_type="string")
                        db_session.add(attribute)

                    for value in values:
                        attr_value = db_session.query(AttributeValue).filter_by(value=value).first()
                        if not attr_value:
                            attr_value = AttributeValue(value=value)
                            db_session.add(attr_value)

                        if attribute not in product.attributes:
                            product.attributes.append(attribute)
                        if attr_value not in product.attributes_values:
                            product.attributes_values.append(attr_value)

                db_session.commit()
            except Exception as e:
                db_session.rollback()
                raise Exception(f"Error updating product attributes: {str(e)}")

    @classmethod
    def get_product_attributes(cls, product_id: int) -> Dict[str, List[str]]:
        """
        Retrieves the attributes and their values for a given product.

        Args:
            product_id (int): The ID of the product.

        Returns:
            Dict[str, List[str]]: Dictionary of attributes and their values.

        Raises:
            Exception: If there's an error retrieving product attributes.
        """
        with cls.session_scope() as db_session:
            try:
                product = db_session.query(Product).get(product_id)
                if not product:
                    raise Exception(f"Product with ID {product_id} not found")

                attributes = {}
                for attr in product.attributes:
                    attributes[attr.name] = [
                        value.value for value in product.attributes_values
                        if value in attr.values
                    ]
                return attributes
            except Exception as e:
                raise Exception(f"Error retrieving product attributes: {str(e)}")