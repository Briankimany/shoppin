
from app.models.vendor_submits import VendorSubmit
from app.data_manager.client_access_manager import session_scope
from app.models.base import VendorRequestStatus

from app.routes.logger import LOG
from app.models.vendor_plans import VendorPlan



class Plan_:
    def __init__(self ,name ,id_ , commision):
        self.name = name    
        self.id = id_ 
        self.price = commision

class VendorRegister:
    get_unique = lambda db_session, attribute , value: db_session.query(VendorSubmit).filter(getattr(VendorSubmit,attribute)==value).first()

    @classmethod
    def get_plans(cls):
         
        with session_scope(commit=False,
                           logger=LOG.VENDOR_LOGGER,
                           func=cls.get_plans) as db_session: 
             
             plans = db_session.query(VendorPlan).all()
             return [Plan_(p.name , p.id ,p.product_commission_percent) for p in plans]


    @classmethod
    def record_registration_request(cls,data:dict,plan=None):
        """
        data = {
         name:<unique name eg vendor1 // shortened name
         first_name :<first name eg John ,
         second_name :second_name eg Doe,
         email: <vendors email> 
         phone: <vendor phone number>
         store_name:<store name>
         payment_type: <pre or post delivery>
         store_description: <describe your store>
        }
        """

        with session_scope(commit=False,
                           logger=LOG.VENDOR_LOGGER,
                           func=cls.record_registration_request) as db_session:
            
      
            
            LOG.VENDOR_LOGGER.info("[REG-REQUEST] Registering vendor. ")
            LOG.VENDOR_LOGGER.debug(f"[REG-REQUEST] Data ={data}")

            if not plan:
                plan = db_session.query(VendorPlan
                                    ).filter(VendorPlan.id == int(data['plan_id'])
                                    ).first()
                data.pop('plan_id')

            request = VendorSubmit(**data)
            request.plan = plan

            passed = True
            
            msg =[]
            if cls.get_unique(db_session,'email',request.email):
                passed = False
                msg.append(f"Email {request.email} already exists\n")

            if cls.get_unique(db_session,"name",request.name):
                passed = False
                msg.append(f"User {request.name} alredy exist.")

            if cls.get_unique(db_session,"store_name",request.store_name):
                passed = False
                msg.append(f"Business Name {request.store_name} alredy exist.")


            if passed:
                db_session.add(request)
                db_session.commit()
                LOG.VENDOR_LOGGER.info('[REG-REQUEST] Registration recorderd')
                return True ,'Request recorded.'
          
            LOG.VENDOR_LOGGER.warning("[REG-REQUEST] Invalid data")
            LOG.VENDOR_LOGGER.debug(f"[REG-REQUEST] data=({data} ,msg={msg})")
            return False ,msg
                
    @classmethod
    def approve_reject_registration(cls,registration_id:int,status = VendorRequestStatus.APPROVED):
            
            LOG.VENDOR_LOGGER.info("Approving vendor.")
            LOG.VENDOR_LOGGER.debug(f"Id={registration_id}")
            with session_scope(commit=False,
                           logger=LOG.VENDOR_LOGGER,
                           func=cls.approve_reject_registration) as db_session:
                
                registration = cls.get_unique(db_session,
                                              'id',registration_id)
                
                registration.status = status
                db_session.commit()
            return True
    
    @classmethod
    def get_vendors_to_review(cls ,filters = ['pending']):
            LOG.VENDOR_LOGGER.info(f"[REG-REVIEW] Reviewing Vendors registration request filters={filters}")
            with session_scope(commit=False,
                    logger=LOG.VENDOR_LOGGER,
                    func=cls.get_vendors_to_review) as db_session:
                
                data = db_session.query(
                     VendorSubmit
                ).filter(
                     VendorSubmit.status.in_([getattr(VendorRequestStatus ,i.upper()) for i in filters])
                ).all()

                LOG.VENDOR_LOGGER.info(f'[REG-REVIEW] Num of requests = {len(data)}')
                for request in data:
                     if request.status == VendorRequestStatus.PENDING:
                          
                          LOG.VENDOR_LOGGER.debug(f"[REG-REVIEW] Updating request to reviewed {request}")
                          request.status = VendorRequestStatus.REVIEWED

                dict_data= [i.to_dict() for i in data]
                db_session.commit()
                return dict_data


    
        
            
                
