
from enum import Enum
import string
from hashids import Hashids
import os 
from dotenv import load_dotenv

load_dotenv()

class PaymentMethod(str, Enum):
    BANK = "Bank"
    MPESA = "M-pesa"
    AIRTEL_MONEY = "Airtel-money"
    INTERNAL_TRANSFER = 'Internal transfer'

class PaymentCategory(str, Enum):
    PRODUCT_SALE = "Product sale"
    VENDOR_WITHDRAWAL_FEE = "Withdrawal fee"
    HOSTING_FEE = "Hosting Fee"
    CHARGES = 'Charges'
    PRODUCT_COMMISSION = "Commission on product"


class WithDrawAvlailableMethods(str, Enum):
    MPESA = "M-pesa"


class ChargeType(str , Enum):
    PRODUCT =   'Product'
    WITHDRAWAL_UNSCHEDULED = 'Unscheduled withdraw'
    WITHDRAWAL_NORMAL = 'Scheduled withdraw'


class PayoutFrequency(str , Enum):
    BI_WEEKLY = "bi-weekly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    THREE_DAY_INTERVAL = "every 3 days"



