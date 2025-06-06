from flask import Blueprint, jsonify, request ,render_template
from app.data_manager.product.product_query import ProductQuery
from app.data_manager.scoped_session import Session 

from .views.shop import (
    ProductListView,
    SpecificProduct)

from .routes_utils import inject_user_data

blueprint = Blueprint('blueprint', __name__)
query = ProductQuery()

def product_static_fields(_id):
    from urllib.parse import urlencode
    
    data = {'category':'Electronics'}
    return urlencode(data) 

@blueprint.context_processor
def inject():
    data= inject_user_data()
    data['get_prod_static_fields'] = product_static_fields
    return data 

def error_response(message, status_code):
    return jsonify({"error": message}), status_code


blueprint.add_url_rule(
    '/products/q',
    view_func=ProductListView.as_view('product_list'),
    methods=['GET']
)
blueprint.add_url_rule(
    '/products/p/details',
    view_func=SpecificProduct.as_view('specific_product'),
    methods = ['GET']
)

@blueprint.route("/products/product/<_id>")
def view_specific_product(_id):
    return render_template(
        'shop/components/products/specific_product.html',
        _id=_id)

@blueprint.route('/products/test')
def test_t():
    return render_template('shop/components/products/grid.html')


@blueprint.route('/products/filters', methods=['GET'])
def get_available_filters():
    """Get all available filter options"""
    try:
        filters = query.get_filter_options()
        return jsonify({"data": filters})
    except Exception as e:
        return error_response(str(e), 500)


@blueprint.route('/products/brands', methods=['GET'])
def get_brands_summary():
    """Get summary of products by brand"""
    try:
     
        brands = query.get_filter_options()
        brands = brands['brand']
      
        return jsonify({"data": brands})
    except Exception as e:
        return error_response(str(e), 500)

@blueprint.route("/products/search/suggestions")
def suggestions():
    query_term = request.args.get('q')
    data= query.search(query_term,True)

    return jsonify({"data":data})

@blueprint.route('/products/search', methods=['GET'])
def search_products():
    """Search products by name"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return error_response("Search term required", 400)
            
        results = query.search(search_term)
        print(results)
        return jsonify({"data": results})
            
    except Exception as e:
        return error_response(str(e), 500)


@blueprint.route('/products/categories')
def categories():
    
    data ={
        "categories": {
            "Electronics": {
            "Home Appliances": {
                "Kitchen": ["Electric Cookers", "Toasters"],
                "Entertainment": ["Screens", "Music Systems"]
            },
            "Microcontrollers": ["Arduinos", "Timing Circuits"]
            },
            "Utensils": {
            "Cooking": ["Pots", "Pans", "Spatulas"],
            "Storage": ["Containers", "Jars"]
            },
            "Clothing": {
            "Men": ["Shirts", "Trousers"],
            "Women": ["Dresses", "Handbags"]
            },
            "Books": {
            "Science": ["Physics", "Chemistry"],
            "Fiction": ["Fantasy", "Thriller"]
            }
        }
        }

    return jsonify({
        "data": {
            "Electronics": {
            "Home Appliances": {
                "Kitchen": ["Toasters", "Blenders", "Microwaves"],
                "Cleaning": ["Vacuum Cleaners", "Steam Mops"]
            },
            "Computers": ["Laptops", "Desktops", "Accessories"]
            },
            "Furniture": {
            "Living Room": ["Sofas", "Coffee Tables"],
            "Bedroom": ["Beds", "Wardrobes"]
            }
        }
        })