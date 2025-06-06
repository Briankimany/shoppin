from .base import *

class SpecificProduct(BaseView):
    """
    View to fetch data about a specific product and suggest similar products
    based on static and dynamic filters.
    """

    def __init__(self):
        super().__init__()
        self.default_per_page = 3

    def _generate_dynamic_filters(self, data):
        """
        Convert static filter dict to query-compatible condition tuples.

        Args:
            data (dict): Static filters like category, brand, etc.

        Returns:
            list[tuple]: List of (op, key, value) conditions.
        """
        return [('eq', key, value) for key, value in data.items()]

    def _extract_static_filters(self, dynamic_filters):
        """
        Extract static filters from request.args by excluding known dynamic and special arguments.
        """
        return {
            key: request.args.get(key)
            for key in request.args
            if key not in list(dynamic_filters.keys()) + self.special_args
        }

    def _decode_product_id(self):
        """
        Extract and decode the obfuscated product ID.

        Returns:
            int: Decoded product ID.

        Raises:
            Exception: If the ID is invalid or not decodable.
        """
        string_id = request.args.get('id', '')
        decoded = self.IdHider.decode(string_id)

        self.logger.debug("[PRODUCT-SPEC] Decoding ID: %s -> %s", string_id, decoded)

        if not decoded:
            self.logger.critical("[PRODUCT-SPEC] Invalid product ID received: %s", string_id)
            raise Exception("Invalid product ID")

        return decoded[0]

    def _fetch_product(self, product_id):
        product = self.query.get_product(product_id=product_id)
        if not product:
            self.logger.error("[PRODUCT-SPEC] No product found with ID: %s", product_id)
            raise Exception("No product found")
        return product

    def _fetch_suggested_products(self, static_filters, dynamic_filters, page, per_page):
        fields = self._generate_dynamic_filters(static_filters)
        self.logger.info("[PRODUCT-SPEC] Static filters: %s", static_filters)
        self.logger.info("[PRODUCT-SPEC] Dynamic filters: %s", dynamic_filters)
        self.logger.debug("[PRODUCT-SPEC] Fetching similar products with: %s", fields)

        return self.query.search2(
            static_data=fields,
            filters=dynamic_filters,
            offset=(page - 1) * per_page,
            limit=per_page
        )

    def get(self):
        """
        Fetches the specific product and related suggestions.

        Returns:
            Response: JSON response containing product and related suggestions.
        """
        try:
            self.logger.info("[PRODUCT-SPEC] Request received for specific product view")

            dynamic_filters = self._parse_filters()
            static_filters = self._extract_static_filters(dynamic_filters)
            page, per_page = self._extract_page_data()

            product_id = self._decode_product_id()
            product_details = self._fetch_product(product_id)

            if not static_filters and not dynamic_filters:
                return jsonify({"data":product_details})
            
            suggested = self._fetch_suggested_products(static_filters, dynamic_filters, page, per_page)

            response_data = {
                "sugessted_products": self._paginate_results(suggested, page, per_page),
                "product_data": product_details,
            }


            self.logger.debug("[PRODUCT-SPEC] Response constructed successfully.")
            return jsonify(response_data)

        except Exception as e:
            self.logger.critical("[PRODUCT-SPEC] Unexpected failure: %s", str(e), exc_info=True)
            return self._error_response(str(e), 400)
