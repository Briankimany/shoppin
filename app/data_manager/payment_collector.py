
import requests
from config.config import JSONConfig
from app.routes.logger import LOG
import time 
from app.data_manager import OrderManager
from app.models_utils import IdHider
from requests  import ConnectionError ,ConnectTimeout

class PaymentProcessor:
    """Handles complete payment flow in one class"""
    
    _config = JSONConfig(json_path='config.json')
    
    @classmethod
    def initiate_payment(cls, phone: str, amount: float, orderid: str) -> tuple:
        """Initiate payment and return invoice_id"""
        invoice_id = None 
        try:
            response = requests.post(
                url=f"{cls._config.payment_url}/pay",
                json={'phone': phone, 'amount': amount, 'orderid': orderid},
                headers={
                    "Authorization": f"Bearer {cls._config.authkey}",
                    "Content-Type": "application/json"
                },
                timeout=7
            )
            
            if response.status_code != 200:
                raise ValueError(f"Payment initiation failed: {response.text}")
                
            invoice_id = response.json().get('response', {}).get('invoice_id')
            if not invoice_id:
                raise ValueError("No invoice_id in response")
                
            return invoice_id
        except ConnectionError as e:
            LOG.ORDER_LOGGER.critical(f"Connection refused {e}")
            return 'pending'
            
        except ConnectTimeout as e:
            LOG.ORDER_LOGGER.error(f'Connection timeout {e}')
            pass 
        except Exception as e:
            LOG.ORDER_LOGGER.error(f"Payment initiation error: {str(e)}")
        finally:
            return invoice_id
        

    @classmethod
    def check_status(cls, invoice_id: str, max_retries: int = 5 ,external_max_retries:int=2) -> str:
        """Check payment status with retries"""
        response=None 
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    url=f"{cls._config.payment_url}/check-status",
                    json={
                        "SIMULATE": False,
                        "MAXRETRIES": external_max_retries,
                        'invoice_id': invoice_id
                    },
                    headers={
                        "Authorization": f"Bearer {cls._config.authkey}",
                        "Content-Type": "application/json"
                    },
                    timeout=5
                )
                
                status = response.json().get('MESSAGE')
                LOG.ORDER_LOGGER.debug(f"Payment status check {attempt+1}/{max_retries} for Invoice ID: {invoice_id} - Status: {status}")

                if status == "COMPLETE":
                    LOG.ORDER_LOGGER.info(f"Payment completed for Invoice id : {invoice_id}")
                    return 'paid'
                elif status == "FAILED":
                    LOG.ORDER_LOGGER.warning(f"Payment failed for Invoice: {invoice_id}")
                    return 'canceled'
                    
                if attempt < max_retries:
                    time.sleep(2)
            
            except ConnectionError as e:
                LOG.ORDER_LOGGER.critical(f"Connection refused {e}")
                return 'failed'
            
            except ConnectTimeout as e:
                LOG.ORDER_LOGGER.error(f'Connection timeout {e}')
                continue

            except Exception as e:
                if response:
                    LOG.ORDER_LOGGER.error(f"Exception occurred in payment collection for invoice: {invoice_id}: error={e} status_code={response.status_code} Latest response:{response.content}")
                else:
                    LOG.ORDER_LOGGER.error(f"Exception occurred in payment collection for invoice: {invoice_id}: error={e}")

        return 'pending'

    @classmethod
    def collect_payment(cls, phone: str, amount: float, orderid: int) -> str:
        """Complete payment flow"""

        order = OrderManager.get_order_by(False ,id=orderid)
        if order and order.tracking_id :
            LOG.ORDER_LOGGER.warning(f"Attempted to initiate a new payment request for order {order}")
            invoice_id = order.tracking_id 
        else:
            LOG.ORDER_LOGGER.info(f"Making a new payment reques for order {order}")
            invoice_id = cls.initiate_payment(phone, amount, IdHider.encode(orderid))

            if not invoice_id:
                return None
            OrderManager.update_order( orderid ,tracking_id=invoice_id)
        
        time.sleep(cls._config.DELAY_BEFORE_STATUS_CHECK)
        return cls.check_status(invoice_id)
