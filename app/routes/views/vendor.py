
from flask.views import MethodView
from flask import request ,jsonify

class SubmitContact(MethodView):

    def post():

        data = request.form
        
        return jsonify({
            "message":"success",
            "data":"Registration under review. Our team will contact you very soon"
        })


