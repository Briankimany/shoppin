"""
Base class for all class-based views (CBVs) under the shop blueprint.

This class provides shared utilities and configurations such as:
- Default pagination logic.
- Query and session management tools.
- Filter parsing for query arguments.
- Error response formatting.
- Product filtering and search integration.
- Logging utilities for debugging and monitoring.

Attributes:
    query (ProductQuery): Service for fetching and filtering product data.
    processor (PaymentProcessorService): Handles payment processing logic.
    session_manager (SessionManager): Manages session-related operations.
    logger (logging.Logger): Shop-specific logger instance.
    default_per_page (int): Default pagination limit.
    IdHider (type): Utility for obfuscating and de-obfuscating IDs.
    static_fields (list): Filter fields considered static (e.g., category).
    special_args (list): Reserved query arguments (e.g., page, id, offset).

Decorators:
    bp_error_logger: Logs uncaught exceptions using SHOP_LOGGER.
    session_set: Injects session context into the request.

Intended for inheritance by views like `SpecificProduct`, `ProductListView`, etc.
"""

from app.routes.logger import LOG
from flask.views import MethodView
from flask import request ,jsonify 
from app.data_manager import ProductQuery ,SessionManager
from app.services.payment_processor import PaymentProcessorService
from app.routes.logger import bp_error_logger 
from app.routes.routes_utils import session_set
from app.models_utils import IdHider

class BaseView(MethodView):

    decorators = [bp_error_logger(LOG.SHOP_LOGGER, 500), session_set]

    def __init__(self):
        self.query = ProductQuery() 
        self.processor = PaymentProcessorService()
        self.session_manager = SessionManager(db_session=None)

        self.logger = LOG.SHOP_LOGGER

        self.default_per_page = 6
        self.IdHider = IdHider

        self.static_fields = ['category']
        self.special_args= ['page','offset','id','per_page']

    def _extract_page_data(self):
        """_summary_
        Extract page data from the requests args.
        if the url contaings (page or page_data) 
        the values will be extracted and if not, the default values
        will be returned.

        Returns:
            tuple: page , per_page
        """
        page = int(request.args.get('page', 1)) 
        per_page = int(request.args.get('per_page', self.default_per_page))

        return page ,per_page


    
    def _error_response(self, message, status_code):
        return jsonify({"error": message}), status_code

    def _parse_filters(self):
        """Parse and validate filter parameters"""
        filters = {}
        for key in request.args:
            if key in self.special_args + self.static_fields:
                continue
            filters.update({key:request.args.getlist(key)})
        
        return filters 

    def _paginate_results(self, products, page, per_page):
        """Paginate the product results"""
        total_products = len(products)
        return {
            "data": products,
            "meta": {
                "total": total_products,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_products + per_page - 1) // per_page
            }
        }

