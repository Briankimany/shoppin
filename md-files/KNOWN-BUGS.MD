
### ***BACKEND KNOWN BUGS***

#### SHOP Blueprint
    - [ ] If a user has two pending orders, the system will always trigger check status for the first order.
    - [ ] If the user never interacted with the pushup,the `PaymentCollector.check_status` will always rerurn `WAITING`.
    
