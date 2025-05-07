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
4. [ ] find a way to separate sessions doing write operations and read operation to avoid roll back errors

---

### **Vendor Backend**
#### **Core Functionality**
1. [x] Login/register system
2. [x] Remove item method
         - [x] make a new column in product table for deactivatin them
         - [x] filter only active products are sent to the frontend
3. [x] `@meet_vendor_requirements` decorator
4. [x] Image uploading system
   - [x] Cloudinary integration 
5. [x] Multi-vendor product tracking 
6. [x] Move `inject_user_data` into route_utils
7. [x] Display total revenue and weekly revenue
8. [x] impliment csrf protection on vendors side
9. [x] impliment csrf protection on user sid
9. [x] impliment csrf protection on shop side


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
4. [ ] Cart migration when a session expires

---

### **Frontend Improvements**
1. [x] Modern CSS:
   - [x] Order history cards
   - [x] Vendor update forms
2. [x] Quick actions:
   - [x] Shop/profile links 
3. [x] Responsive fixes
4. [ ] check inspection is messed up
5. [ ] Bring items displayed in the cart page and checkout page togehter

#### **vendor front-end**
1. [ ] Improve the landing page for vendor details
2. [ ] Desing the footer for the vendor base template
3. [ ] Add product css button

---

### **Security & Compliance**
1. [ ] Account verification:
   - [ ] Email token system 
   - [ ] Rate limiting
2. [x] GDPR:
   - [x] Consent tracking
   - [x] Data access logging
   
---

### **Bug Fixes**
1. [x] Order status typo (`pendig` → `pending`)
2. [x] User-vendor linking 
3. [ ] Report endpoints 
4. [x] Display correct currency
5. [ ] Fixed edit product for vendors

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




### ✅ **Appended from April 22 **

---

### **Core Systems**
#### **Error Logger & Blueprint System**
5. [x] Added `MAIL_LOGGER`, `SESSIONS_LOGGER` for domain-specific logging  
6. [x] Session and cart creation logs now handled via `LOG` objects  
7. [x] `bp_error_logger` updated with dynamic error messages and dev-safe output  

#### **Database & Models**
4. [x] Added `is_active` column to `Product` table (Boolean, default=True)  
5. [x] Product timestamp fields now use UTC with timezone awareness  
6. [x] `session_tracking.expires_at` uses timezone-aware default  
7. [x] Created scoped session context manager (`session_scope`) to isolate commits and handle rollback safely  
8. [x] Session writing/reading now separated using `session_scope()`  

---

### **Vendor Backend**
#### **Core Functionality**
2. [x] Remove item method  
    - [x] `is_active` column used to deactivate products instead of deleting  
    - [x] Queries now filter using `is_active=True`  
8. [x] CSRF protection implemented in vendor blueprint using Flask-WTF  

---

#### **Payments & Withdrawals**
4. [x] Improved withdrawal status check using HTTP with error logging and JSON fallback  
5. [x] Added POST support to withdrawal status check route  
6. [x] Withdrawal endpoint handles phone formatting, logging, and fallback handling  

---

### **User Features**
3. [x] Password reset:
   - [x] Logging added for password reset attempts
   - [x] Centralized token logic with expiry
   - [x] Updated CSRF-safe view flow

---

### **Frontend Improvements**
#### **vendor front-end**
3. [x] Delete product modal with confirmation (HTML/CSS/JS added)
4. [x] Toast notifications added for async UX feedback
5. [x] Password strength meter + JS validation for registration
6. [x] Fetch-based login/register form handling (error-aware and dynamic)

---

### **Security & Compliance**
3. [x] CSRF Protection:
   - [x] Vendor routes
   - [x] User login/reset flow
   - [x] Error handler with safe JSON fallback

---

### **Bug Fixes**
5. [x] Fixed edit product route to return JSON response and log updates  

---

### **Technical Debt**
4. [x] Separated session read/write logic using scoped sessions to prevent rollback errors  

---


new to todos
impliment the fees calculation mechanism
limit request to certain urls