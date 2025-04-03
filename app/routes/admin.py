
from flask import Blueprint, jsonify, render_template ,request
from sqlalchemy import inspect
from app.create_database import reset_table, init_db ,init_engine
from app.data_manager.vendor import VendorObj
from app.routes.routes_utils import db_session, engine
from app.services.upload import ImageManager
from pathlib import Path
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
inspector = inspect(engine)

@admin_bp.route("/")
def admin_home():
    return render_template('admin.html')

@admin_bp.route("/dashboard")
def dashboard():
    all_data = {}
    for vendor_id in [1, 2, 3, 4]:
        all_data[vendor_id] = VendorObj.summarize_vendors(db_session, vendor_id)
    return render_template("admin/inspect_vendors.html", all_data=all_data)

@admin_bp.route("/get_tables")
def get_tables():
    """Fetch all table names from the database."""
    try:
        tables = inspector.get_table_names()
        return jsonify({"tables": tables})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/reset_table/<string:table_name>", methods=["POST"])
def reset_table_route(table_name):
    """Reset the selected table by truncating it."""
    try:
        reset_table(table_name=table_name)
        return jsonify({"message": f"Table '{table_name}' reset successfully"})
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/init_db", methods=["POST"])
def init_db_route():
    init_db()
    return jsonify({"success": "Database initialized"}), 200

@admin_bp.route("/get-images")
def migrate_images():
    json_file = Path(ImageManager.config.json_path.parent) /'temp_images.json'
    images_data = ImageManager.load_migration_images(db_sessoin=db_session,
                                                     json_file=json_file)

    return jsonify({"data":images_data}) ,200

@admin_bp.route("/update-images-url" , methods = ['POST'])
def update_image_src():
    try:
        data = request.get_json()
        image_data = data['data']
        result =ImageManager.update_images_src_links(db_session=db_session
                                            ,image_data=image_data)
        return jsonify(result) ,200
    except Exception as e:
        print(e)
        return jsonify({"err":str(e)}) ,500
        
