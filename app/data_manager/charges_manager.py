
from typing import Dict, List ,Union
from decimal import Decimal

from sqlalchemy.orm import Session 
from app.models import (
    Charge, 
    Order,
    Payment,
    Product, 
    Vendor,
    Payment,
    VendorCharge,
    ProductCharge)

from .payments import  PaymentManager 
from app.models.model_utils import ChargeType, PaymentMethod, PaymentCategory ,PayoutFrequency
from app.models.charges_utils import Payee
from .client_access_manager import session_scope

from app.routes.routes_utils import LOG
from datetime import datetime


class WithdrawalScheduler:
    """Handles withdrawal scheduling logic and verification"""
    
    @classmethod
    def is_scheduled_withdrawal_day(cls, vendor:Vendor) -> bool:
        """Determine if today is a scheduled withdrawal day"""
        today = datetime.now().date().day
        frequency = vendor.plan.payoutfrequency
        
        if frequency == PayoutFrequency.BI_WEEKLY:
            return today % 14 in {0, 1, 13}
        elif frequency == PayoutFrequency.MONTHLY:
            return today % 28 in {0, 1, 2, 3, 25, 26, 27}
        elif frequency == PayoutFrequency.WEEKLY:
            return today % 7 in {0, 1, 2, 6}
        elif frequency == PayoutFrequency.THREE_DAY_INTERVAL:
            return today % 3 == 0
        else:
            raise ValueError(f"Unsupported payout frequency: {frequency}")

    @classmethod
    def get_withdrawal_charge_type(cls, vendor:Vendor) -> ChargeType:
        """Determine appropriate charge type for withdrawal"""
        if cls.is_scheduled_withdrawal_day(vendor):
            return ChargeType.WITHDRAWAL_NORMAL
        return ChargeType.WITHDRAWAL_UNSCHEDULED
    
class ChargeRuleManager:
    """Handles creation and management of charge rules"""
    
    @classmethod
    def create_product_charge_rule(
        cls,
        db_session: Session,
        percentage: Decimal,
        product_id: int,
        payee: Payee
    ) -> dict:
        """Create a product charge rule with validation"""

        if payee.entity_type == 'product':
            assert payee.entity_id == product_id
        else:
            product = db_session.query(Product).get(product_id)
            assert product is not None
            assert product.vendor.id == payee.entity_id

       
        existing = cls.get_charge_rules(
            db_session,
            type=ChargeType.PRODUCT,
            recipient_id=product_id
        )
        if existing:
            if existing[0].percentage == 100:
                print(f"Product {product_id} already has full coverage charge")
                return existing[0].to_dict()

        charge = Charge(
            type=ChargeType.PRODUCT,
            percentage=percentage,
            recipient_id=product_id,
            payee=payee
        )
        db_session.add(charge)
        db_session.flush()
        
        ChargeRecorder.record_child_charge(db_session, charge, payee)
        
        return charge.to_dict()

    @classmethod
    def get_charge_rules(
        cls,
        db_session: Session,
        **filters
    ) -> List[Charge]:
        """Query charge rules with filters"""
        conditions = [(getattr(Charge, key) == value) for key, value in filters.items()]
        print(filters)
        return db_session.query(Charge).filter(*conditions).all()

class ChargeRecorder:
    """Handles recording actual charge applications"""
    
    @classmethod
    def record_child_charge(
        cls,
        db_session: Session,
        charge: Charge,
        payee: Payee,
    ) -> Union[ProductCharge, VendorCharge]:
        
        """Record a charge application to the appropriate entity"""
        if payee.entity_type == "product":
            child_charge = ProductCharge(charge=charge, 
                                         product_id=payee.entity_id)
        elif payee.entity_type == "vendor":
            child_charge = VendorCharge(charge=charge, 
                                        vendor_id=payee.entity_id,
                                         product_id=charge.recipient_id)
        else:
            error = f"Invalid payee: {payee} for charge: {charge}"
            LOG.DB.error(f"[CHARGE] {error}")
            raise ValueError(error)
        
        db_session.add(child_charge)
        return child_charge

    @classmethod
    def record_withdrawal_charge(
        cls,
        db_session: Session,
        vendor_id: int,
        amount: Decimal,
    ) -> Payment:
        with session_scope() as db_session:
       
            vendor = db_session.query(Vendor).filter_by(id=vendor_id).first()
            if not vendor or not vendor.plan:
                raise ValueError("Vendor or vendor plan not found")

            charge_type = WithdrawalScheduler.get_withdrawal_charge_type(vendor)
            is_scheduled = charge_type == ChargeType.WITHDRAWAL_NORMAL
            
            assert vendor.plan is not None

            plan = vendor.plan
            if amount <= plan.min_payout_threshold:
                fee = (plan.scheduled_withdrawal_flat_fee if is_scheduled 
                    else plan.unscheduled_withdrawal_flat_fee)
            else:
                percentage = (plan.scheduled_withdrawal_percentage if is_scheduled 
                            else plan.unscheduled_withdrawal_percentage)
                fee = amount * percentage
                max_fee = (plan.max_scheduled_withdrawal_fee if is_scheduled 
                        else plan.max_unscheduled_withdrawal_fee)
                fee = min(fee, max_fee)

            PaymentManager.record_payment(
        
                source=f'vendor-{vendor.id}',
                recipient=f'platform',
                amount=fee ,
                method=PaymentMethod.INTERNAL_TRANSFER,
                category=PaymentCategory.CHARGES,
                description=f"{'Scheduled' if is_scheduled else 'Unscheduled'} withdrawal charges"
            )
            
            return fee + amount
    
    @classmethod
    def calculate_vendor_product_fee(cls,product:Product
                                      ,db_session:Session): 
        if not isinstance(product,Product):
            product = db_session.query(Product).filter_by(id=product).first()
            if not product:
                raise Exception(f"Invalid product id")
        
        vendor_charge = db_session.query(Charge).filter(
            Charge.type==ChargeType.PRODUCT,
            Charge.recipient_id == product.id,
            Charge.payee == Payee('vendor',product.vendor_id)
        ).first()

        if not vendor_charge:
            LOG.VENDOR_LOGGER.debug(f"[CHARGES] Charge not covered by vendor {product}")
            return 
        
        return  vendor_charge.apply_charge( product.vendor.plan.product_commission(product.price)) 
    
    @classmethod
    def record_products_commision(cls,order_id,session_tkn:str=None):
        with session_scope(func=cls.record_products_commision) as db_session:

            order = db_session.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise Exception("Invalid order id")
            
            commission_charges ={}
            records =[]

            for order_item in order.orderitems:
                product_commision = order_item.quantity*order_item.product.commission

                if order_item.product.vendor_id not in commission_charges:
                    commission_charges[order_item.product.vendor_id]=[]
                commission_charges[order_item.product.vendor_id].append(product_commision)

                records.append(
                         {"source":f'product-{order_item.product.id}',
                        "recipient":'platform',
                        "session_tkn":session_tkn,
                        'amount':product_commision,
                        'method':PaymentMethod.INTERNAL_TRANSFER,
                        'category':PaymentCategory.PRODUCT_COMMISSION,
                        'description':"Product's commision covered by product."
                        })  
            PaymentManager.record_payments_batch(records)
            LOG.SHOP_LOGGER.debug(f"[COMMISSION] Data from id {order_id} : {commission_charges}")
            return {vendor_id:sum(charges) for vendor_id,charges in commission_charges.items()} 

    @classmethod
    def record_products_charges(cls,order_id:int,session_tkn:str=None)->Dict:
        """
        Record a product charge to  vendors asssociated to a certain order after  a succesfull purchase.
        """

        with session_scope(func=cls.record_products_charges) as db_session:

            order = db_session.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise Exception("Invalid order id")
            
            charges = []
        
            vendors_data={}
            for order_item in order.orderitems:
       
                fee  = cls.calculate_vendor_product_fee(product= order_item.product,
                                                        db_session=db_session)
                
                
                if not fee:
                    continue
        
                if order_item.product.vendor_id not in vendors_data:
                    vendors_data[order_item.product.vendor_id]=[]
                vendors_data[order_item.product.vendor_id].append(fee)

                charges.append({
                    "source":f'vendor-{order_item.product.vendor_id}',
                    "recipient":'platform',
                    'session_tkn':session_tkn,
                    'amount':fee,
                    'method':PaymentMethod.INTERNAL_TRANSFER,
                    'category':PaymentCategory.CHARGES,
                    'description':"Product's commision covered by vendor."
                    }
                )
            PaymentManager.record_payments_batch(data=charges)
            return {vendor_id:sum(vendors_data[vendor_id]) for vendor_id in vendors_data}


        
        

