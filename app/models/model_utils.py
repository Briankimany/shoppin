
from enum import Enum


class PaymentMethod(str, Enum):
    BANK = "Bank"
    MPESA = "M-pesa"
    AIRTEL_MONEY = "Airtel-money"

class PaymentCategory(str, Enum):
    PRODUCT_SALE = "Product sale"
    VENDOR_FEE = "Vendor fee"
    HOSTING_FEE = "Hosting Fee"
