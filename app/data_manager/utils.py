
from enum import Enum

class ComisionStrategy(str , Enum):
    USER_PAID = 'User paid'
    COST_SHARED = 'Cost shared'
    VENDOR_PAID = 'Vendor paid'