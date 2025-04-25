
from flask.views import MethodView
from flask import request ,jsonify ,render_template
from app.data_manager.vendor_registration import VendorRegister
from app.routes.logger import LOG
from app.routes.routes_utils import session_set
from pprint import pprint

class SubmitContact(MethodView):

    decorators = [session_set]
    def post(self):

        data = request.form.to_dict()

        data['name'] = data['first_name']
        data['agreed_terms'] = data['terms'] == 'on'

    
        data.pop('csrf_token')
        data.pop('terms')
  
        registered = VendorRegister.record_registration_request(
            data,
            plan=None
        )
        return jsonify({
            "message":"success" if registered[0] else 'error',
            "data":"You we reach out to you with your account" if registered[0] else registered[1],
            'url':"#"
        }) ,200 if registered[0] else 400
    
class HomeView(MethodView):
    def get(slef):
        plans = VendorRegister.get_plans()
        return render_template('vendor/home.html',vendor_plans = plans)



