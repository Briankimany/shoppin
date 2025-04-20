### **Track Changes**

---

### **Core Systems**
#### **Error Logger & Blueprint System**  
1. [x] Universal `@bp_error_logger` decorator for all blueprints  
2. [x] Blueprint-specific logging (e.g., `LOG.SHOP_LOGGER`)   
3. [x] error template (`error.html`)
   - [x] Styled error message display  
   - [x] "Go Back" button  
   - [x] Error code visibility  
4. [x] Debug/production mode safety (hide sensitive errors)  
5. [x] Customizable HTTP status codes per route  

#### **Database & Models**
1. [x] Added `ClientAccessLog` table (replaces IP columns in `session_tracking`)
   - [x] `consent_given` (Boolean, default=False)  
   - [x] `accessed_at` (DateTime)
2. [x] Added to `vendorpayout`:
   - [x] `tracking_id`, `batch_id`, `updated_user_id` columns
3. [x] Fixed tempfile items not in database 

---

### **Vendor Backend**
#### **Core Functionality**
1. [x] Login/register system
2. [ ] Remove item method
3. [x] `@meet_vendor_requirements` decorator
4. [x] Image uploading system
   - [x] Cloudinary integration 
5. [x] Multi-vendor product tracking 

#### **Order Management**
1. [x] Fix adding products after failed checkout 
2. [x] Stock reduction on successful checkout 
3. [x] Group products in vendor UI 
4. [x] Vendor/order endpoint fixes 
5. [x] Formatted order history (`get_format_recent_orders`)
6. [x] Detailed order breakdowns (`specific_order_details`)

#### **Payments & Withdrawals**
1. [x] Payment table records (#18)
2. [x] Withdraw system improvements:
   - [x] `WithDrawAvailableMethods` enum 
   - [x] `MAX_NUM_PENDING_WITHDRAWs` limit 
   - [x] Status check automation 
3. [ ] Withdraw email notifications 
4. [ ] Vendor withdrawal history endpoint 

---

### **User Features**
1. [x] Profile system:
   - [x] Edit functionality 
   - [x] Vendor portal link 
2. [x] Order system:
   - [x] Preview fixes 
   - [ ] Status refresh button
3. [x] Password reset:
   - [x] Gmail integration
   - [ ] Mailgun integration

---

### **Frontend Improvements**
1. [x] Modern CSS:
   - [x] Order history cards
   - [x] Vendor update forms
2. [x] Quick actions:
   - [x] Shop/profile links 
3. [x] Responsive fixes

---

### **Security & Compliance**
1. [ ] Account verification:
   - [ ] Email token system (#22)
   - [ ] Rate limiting
2. [x] GDPR:
   - [x] Consent tracking
   - [x] Data access logging

---

### **Bug Fixes**
1. [x] Order status typo (`pendig` → `pending`)
2. [x] User-vendor linking 
3. [ ] Report endpoints 

---

### **Technical Debt**
1. [ ] Mailgun email integration
2. [ ] Withdrawal history UI
3. [ ] Report generation system


#### **HTML Restructuring**

1. **Admin**
    - admin.html
    - inspect_vendor.html

2. **Login**
    - login.html

3. **Shop**
    - shops.html
    - payment.html
    - products.html
    - specific_product.html
    - cart.html
    - checkout2.html

4. **User**
    - orders.html
    - profile.html (needs fixing)
    - forgot_password.html
5. **Vendor**
    - base2.html
    - home.html
    - update_details.html
    - dashboard2.html
    - add_product.html
    - edit_product.html
    - payout.html
    - products.html

