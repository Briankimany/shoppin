
from .base import *


class ProductListView(BaseView):

    def __init__(self):
        super().__init__()
        
    
    def get(self):
        """Handle GET requests for product listing"""
        try:
           
            page ,per_page = self._extract_page_data()

            filters = self._parse_filters()

            products = self.query.filter_products(filters ,offset=(page-1)*self.default_per_page ,limit=self.default_per_page)
            print("Returning products",len(products))
    
            response_data = self._paginate_results(products, page, per_page)
            
            return jsonify(response_data)

        except ValueError as e:
            self.logger.error(f"[PRODUCTS-LIST] Value error  {e}")
            return self._error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"[PRODUCTS-LIST] Could not fetch products list {e}")
            return self._error_response(str(e), 500)
