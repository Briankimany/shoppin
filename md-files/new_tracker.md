
BUGS
- AFTER DEACTIVATING A PRODUCT AND USERSHAVE NOT REFRESHED THEIR PAGES
- Change most of the logging level to debug instead of info

FEATURES
- Annalytics for vendor
    which product is clicked most
    which vendor is most visited
    how many orders are fullfield
    discounts ,bundle sales
    list and mazimize the products visibility
    marketin support with charges
    connect user and vendors for vendor specific enquires
    background async js funcion to check the status of pending orders

- Nofication to deliver products
- update the users ips last seen and improve the ua parsing
- common market for everyone
- To biuld trust we will first set the products to be pay on delivery
QUESTIONS TO ANSWER
1. How do we eatn trust from the users



MANUAL TODOS
- [ ] Apply vendor plan charges on withdraws and commisoin on products
- [ ] Categorize products into smaller subsets and give them tags
- [ ] Redesing the shop home page
- [ ] Apply the user clearance levels to add an enpoint to the admin's dashboard


# Charge & Commission Management System

## Core Objectives
- [ ] Apply automatic charges during product sales
- [ ] Calculate commissions during product creation
- [ ] Support 3 commission strategies:
  - User-paid (100% to customer)
  - Cost-shared (split vendor/user)
  - Vendor-paid (100% to vendor)
- [ ] Handle withdrawal charges (scheduled/unscheduled)

## Database Structure

### `Charge` Model
```python
class Charge(TimeStampedBase):
    __tablename__ = 'charges'
    
    id = Column(Integer, primary_key=True)
    type = Column(Enum('product', 'withdrawal_normal', 'withdrawal_unscheduled'))
    percentage = Column(Numeric(5,2))  # 0.00-100.00
    recipient_id = Column(Integer)  # product_id/vendor_id
    payee_id = Column(String)  # VEND-vendor_id/PROD-product_id
```

### `Payment` Records
```python
{
    'transaction_ref': str,
    'source': str,
    'recipient': str,  # ADMIN_ID
    'amount': int,
    'method': PaymentMethod.INTERNAL_TRANSFER,
    'category': PaymentCategory.CHARGES,
    'description': str
}
```

## Business Rules

### Product Commissions
| Strategy        | Type    | Recipient | Payee    | %   | Price Adjustment |
|-----------------|---------|-----------|----------|-----|------------------|
| **User-paid**   | product | product   | product  | 100 | Included in price|
| **Cost-shared** | product | product   | product  | X%  | Partial          |
|                 | product | product   | vendor   | Y%  | Deduct from vendor|
| **Vendor-paid** | product | product   | vendor   | 100 | Deduct from vendor|

**Calculation:**
```python
commission = (
    product_price * plan.product_commission 
    if product.price >= plan.min_price_threshold 
    else plan.product_flat_fee
)
```

### Withdrawal Charges
| Type           | Charged To | Percentage Source |
|----------------|------------|-------------------|
| Normal         | Vendor     | Admin-configured  |
| Unscheduled    | Vendor     | Admin-configured  |

## `ChargesManager` Class

### Key Methods
1. **CRUD Operations**
   - Manage charge rule records

2. **Commission Calculation**
   ```python
   def calculate_shared_commissions(product_ids: list) -> Dict[int, float]:
       """Returns {vendor_id: amount_to_deduct} for cost-shared products"""
   ```

3. **Balance Adjustment**
   ```python
   def apply_charge(
       vendor_id: int, 
       amount: float, 
       charge_type: str, 
       session: Session
   ) -> bool:
       """Uses update_vendor_balance()"""
   ```

### Process Flow
1. **Product Creation**:
   - Determine commission strategy
   - Create charge rule(s)
   - Adjust product price if user-paid

2. **Withdrawal**:
   - Identify charge type
   - Apply percentage to amount
   - Deduct from vendor balance
   - Record payment to admin

## Technical Notes
- Uses existing `session_scope` context manager
- Admin account treated as special vendor
- Charge table stores rules, not transactions
- Withdrawal rates set administratively
