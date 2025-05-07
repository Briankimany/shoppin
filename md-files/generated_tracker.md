### **Track Changes**

---

### **Backend**
#### **Core Systems**
1. [x] Universal `@bp_error_logger` decorator for all blueprints  
2. [x] Blueprint-specific logging (e.g., `LOG.SHOP_LOGGER`)  
3. [x] Error template (`error.html`) with styled display, "Go Back" button, and error codes  
4. [x] Debug/production mode safety (hide sensitive errors)  
5. [x] Customizable HTTP status codes per route  
6. [x] Added `MAIL_LOGGER`, `SESSIONS_LOGGER` for domain-specific logging  
7. [x] Session and cart creation logs via `LOG` objects  
8. [x] `bp_error_logger` updated with dynamic error messages  

#### **Database & Models**
1. [x] Added `ClientAccessLog` table (replaces IP columns in `session_tracking`)  
   - [x] `consent_given` (Boolean)  
   - [x] `accessed_at` (DateTime)  
2. [x] Added to `vendorpayout`: `tracking_id`, `batch_id`, `updated_user_id`  
3. [x] Fixed tempfile items not in database  
4. [x] Added `is_active` column to `Product` table (Boolean, default=True)  
5. [x] Timezone-aware timestamps for Product/SessionTracking  
6. [x] Scoped session context manager (`session_scope`) for rollback safety  
7. [x] Separated session read/write operations  

#### **Vendor Backend**
1. [x] Login/register system  
2. [x] Remove item method (uses `is_active` column)  
3. [x] `@meet_vendor_requirements` decorator  
4. [x] Image uploading with Cloudinary  
5. [x] Multi-vendor product tracking  
6. [x] CSRF protection (vendor side)  
7. [x] Order management fixes (stock reduction, grouping, endpoints)  
8. [x] Payment/withdrawal system improvements  
9. [ ] Apply charges from the plans table

#### **Payments & Withdrawals**
1. [x] Payment table records  
2. [x] Withdraw system:  
   - [x] `WithDrawAvailableMethods` enum  
   - [x] `MAX_NUM_PENDING_WITHDRAWs` limit  
   - [x] Status check automation  
3. [ ] Withdraw email notifications  
4. [ ] Vendor withdrawal history endpoint  

#### **User Features**
1. [x] Profile system (edit, vendor portal link)  
2. [x] Order system (preview fixes)  
3. [x] Password reset:  
   - [x] Gmail integration  
   - [ ] Mailgun integration  
4. [ ] Cart migration on session expiry  

---

### **Frontend**
#### **User-Facing**
1. [x] Modern CSS for order history/vendor forms  
2. [x] Quick action links  
3. [x] Responsive fixes  
4. [x] Cart/checkout UI improvements  

#### **Vendor-Facing**
1. [x] Delete product modal with confirmation  
2. [x] Toast notifications for async actions  
3. [x] Password strength meter + validation  
4. [x] Fetch-based form handling  
5. [ ] Improve vendor landing page  
6. [ ] Design footer for vendor template  

#### **Security & Compliance**
1. [x] CSRF protection (vendor/user flows)  
2. [x] GDPR compliance (consent tracking, data logging)  
3. [x] Account verification:  
   - [x] Email token system  
   - [ ] Rate limiting  

---

### **Bug Fixes**
1. [x] Order status typo (`pendig` → `pending`)  
2. [x] User-vendor linking  
3. [ ] Report endpoints  
4. [x] Display correct currency  
5. [x] Edit product route fixes  

---

### **New TODOs**
1. Implement fees calculation mechanism  
2. Rate limiting for sensitive URLs  
3. Session/cart migration logic  
. With4drawal history UI  