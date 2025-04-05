### **Track Changes**

#### **Vendor Backend**
- **[x] 1.** Add login and register functionality
- **[ ] 2.** Add the remove item method
- **[x] 3.** Add the "meet vendor requirements" decorator
- **[x] 4.** Implement image uploading
- **[x] 5.** Fix vendor tracking of individual products from users buying from multiple vendors
- **[x] 6.** Remove duplicate HTML files
- **[ ] 7.** Fix the ability to add products after an initial checkout fails
- **[x] 8.** Reduce stock quantity after successful checkout (update the values after setting the order to "paid")
- **[x] 9.** Group products in the vendor's edit page, shop
- **[ ] 10.** Automatic upload of images to the remote server and clear space in the static folder
    - Images are stored on PythonAnywhere until manual triggering to upload to Cloudinary
- **[x] 11.** Password resetting:
    - Mailgun emailing
    - Gmail
- **[ ] 12.** Add edit profile functionality
- **[ ] 13.** Fix order preview on user pages
- **[ ] 14.** Fix the update detail endpoint for vendors
- **[ ] 15.** Fix tracking user data
- **[x] 16.** Fix tempfile having items not in the database
- **[ ] 17.** Link the user table and vendor via the user ID
- **[ ] 18.** Fill the payment table with records from successful checkout
- **[ ] 19.** Fix the vendor/order endpoint
- **[ ] 20.** Fix vendor withdrawal history endpoint
- **[ ] 21.** Fix endpoint for reports

---

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

