from flask import request, jsonify
from flask.views import MethodView
from app.data_manager.product_manager import ProductQuery


class ProductListView(MethodView):
    def __init__(self):
        self.query = ProductQuery()
        self.default_per_page =6
        self.special_args= ['page','offset']

    def _error_response(self, message, status_code):
        return jsonify({"error": message}), status_code

    def _parse_filters(self):
        """Parse and validate filter parameters"""
        filters = {}
        for key in request.args:
            if key in self.special_args:
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

    def get(self):
        """Handle GET requests for product listing"""
        try:
            # Parse pagination parameters
            page = int(request.args.get('page', 1)) 
            per_page = int(request.args.get('per_page', self.default_per_page))

            filters = self._parse_filters()

            products = self.query.filter_products(filters ,offset=(page-1)*self.default_per_page ,limit=self.default_per_page)
            print("Returning products",len(products))
    
            response_data = self._paginate_results(products, page, per_page)
            
            return jsonify(response_data)

        except ValueError as e:
            return self._error_response(str(e), 400)
        except Exception as e:
            return self._error_response(str(e), 500)
