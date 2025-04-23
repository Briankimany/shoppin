
from flask.views import MethodView
from flask import jsonify ,request ,redirect ,url_for

from app.data_manager.token_manager import AcctivationTokenManager as ACM ,LOG

class VerifyAccount(MethodView):

    def get(self):
        data= self.__dict__
        data.update(request.args)

        destination = request.args.get('dst')
        token  = request.args.get("token")

        if not destination or not token:
            return jsonify({"message":"error",'data':"invalid url"})

        allowed_args = ['token', 'dst']
        provided_args = list(request.args.keys())
        
        for i in provided_args:
            if i not in allowed_args:
                return jsonify({"message":"error" ,'data':"invalid arguments"}),400
        
        account_verified = ACM.verify_account_token(token)

        data = "Account verified" if account_verified else "Error occured during verification"
        message = 'success' if account_verified else 'error'
        data = {"message":message ,"data":data}

        LOG.USER_LOGGER.debug(f"[VERIFICATION] account verified {data}")
        LOG.USER_LOGGER.debug("*"*35)

        if account_verified:
            return redirect(url_for ("user.profile"))
        else:
            return redirect(url_for("user.login"))
    
