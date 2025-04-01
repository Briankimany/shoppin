# main.py
from flask import Flask, jsonify, request , session , render_template
from sqlalchemy import text
from app.routes.vendor import vendor_bp , db_session , engine , VendorObj
from app.routes.shop import shop_bp
from app.routes.user import user_bp
from app.routes.info import info_bp
from pathlib import Path
from sqlalchemy import inspect


from app.create_database import reset_table , init_db 
inspector = inspect(engine)


app = Flask(__name__ ,static_folder= str(Path().cwd()/"app/static"))
app.secret_key = "djk"

app.register_blueprint(vendor_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(user_bp)
app.register_blueprint(info_bp)


@app.route("/log")
def log_out():
    session.clear()
    return "Bye"

@app.route("/")
def g():
    return "".join([f"<br> {k}: {v}</br>" for k,v in session.items()])

@app.route('/admin')
def adimin():
    return render_template('admin.html')

@app.route("/get_tables", methods=["GET"])
def get_tables():
    """Fetch all table names from the database."""
    try:
        tables = inspector.get_table_names()
    
        return jsonify({"tables": tables})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset_table/<string:table_name>", methods=["POST"])
def reset_table(table_name):
    """Reset the selected table by truncating it."""
    try:
        reset_table(table_name=table_name)
        return jsonify({"message": f"Table '{table_name}' has been reset successfully."})
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
@app.route('/init_db' , methods = ['GET' , 'POST'])
def initdb():
    init_db()
    return jsonify({"success":"done"}) , 200




@app.route("/admin/dashboard")
def admin_dashboard():
    all_data = {}
    for vendor_id in [1, 2, 3, 4]:
        all_data[vendor_id] = VendorObj.summarize_vendors( db_session,vendor_id)
    print(all_data)
    return render_template("admin/inspect_vendors.html", all_data=all_data)
