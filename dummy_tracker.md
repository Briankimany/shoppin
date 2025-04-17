### **Track Changes**

#### **Vendor Backend**
- **[x] 1.** Add login and register functionality
- **[ ] 2.** Add the remove item method
- **[x] 3.** Add the "meet vendor requirements" decorator
- **[x] 4.** Implement image uploading
- **[x] 5.** Fix vendor tracking of individual products from users buying from multiple vendors
- **[x] 6.** Remove duplicate HTML files
- **[x] 7.** Fix the ability to add products after an initial checkout fails
- **[x] 8.** Reduce stock quantity after successful checkout (update the values after setting the order to "paid")
- **[x] 9.** Group products in the vendor's edit page, shop
- **[x] 10.** Automatic upload of images to the remote server and clear space in the static folder
           - Images are stored on PythonAnywhere until manual triggering to upload to Cloudinary
- **[x] 11.** Password resetting:
    - Mailgun emailing
    - Gmail
- **[ ] 12.** Add edit profile functionality
- **[ ] 13.** Fix order preview on user pages
- **[ ] 14.** Fix the update detail endpoint for vendors
- **[ ] 15.** Fix tracking user data
- **[x] 16.** Fix tempfile having items not in the database
- **[x] 17.** Link the user table and vendor via the user ID
- **[x] 18.** Fill the payment table with records from successful checkout
- **[ ] 19.** Fix the vendor/order endpoint
- **[ ] 20.** Fix vendor withdrawal history endpoint
- **[ ] 21.** Fix endpoint for reports
- **[ ] 22.** Add account authentication on creation of account ie send a token to verify account and add a rate limit
- **[ ] 23.** Add a button in the checkout page that allows user to refresh the status of their cart. This is handy in cases where the user paid but the server was already done checking the status.
Here is your list reformatted in the specified style:

- **[x] 22.** Cleaned up the config initiation in withdraw; added new enum class `WithDrawAvlailableMethods(str, Enum)` for account info starting with 2547  
- **[x] 23.** Limited withdraw options using a new config variable `MAX_NUM_PENDING_WITHDRAWs`; capped at 3 pending withdraws if total amount is below threshold  
- **[x] 24.** Added columns `tracking_id`, `batch_id`, `updated_user_id` to the `vendorpayout` table  
- **[x] 25.** Modified external API return values for single transfer initiation and bulk initiation  
- **[x] 26.** Added method `is_allowed_withdraw` to the `Vendor` object class  
- **[x] 27.** Refactored withdraw logic to initiate request first, then record transaction  
- **[x] 28.** Removed try block in `process-pay` endpoint in vendor blueprint; replaced with `bp_error_logger` decorator  
- **[x] 29.** Added new class in `config.environ_variables` to handle withdraw status tracking  
- **[x] 30.** Added timed status check trigger after initiating a withdraw  
- **[x] 31.** Implemented withdraw request status check logic  


### **Error Logger & Blueprint System**  
- **[x] 1.** Universal `@bp_error_logger` decorator for all blueprints  
- **[x] 2.** Blueprint-specific logging (e.g., `LOG.SHOP_LOGGER`)   
- **[x] 3.** Production-ready error template (`error.html`):  
    - **[x]** Styled error message display  
    - **[x]** "Go Back" button  
    - **[x]** Error code visibility  
- **[x] 5.** Debug/production mode safety (hide sensitive errors)  
- **[x] 6.** Customizable HTTP status codes per route  



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
