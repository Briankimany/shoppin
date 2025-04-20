
from flask import request ,render_template ,jsonify ,Blueprint
from user_agents import parse as parse_user_agent
import requests

from app.data_manager.client_access_manager import ClientAccessManager

from config.config import JSONConfig
from app.routes.logger import LOG ,bp_error_logger
from app.routes.routes_utils import session_set ,meet_vendor_requirements

config = JSONConfig('config.json')

ip_bp = Blueprint('ips', __name__,url_prefix='/ips')


def get_geo_info(ip_address):
    response = requests.get(config.ip_url.format(ip_address))
    return response.json()


def log_geo_data(ip_addr):
    ua = parse_user_agent(request.headers.get("User-Agent", ""))
    geo = get_geo_info(ip_addr)

    ClientAccessManager.log_access({
        "ip_address":ip_addr,
        "proxy": geo.get("proxy", False),
        "country": geo.get("country"),
        "region": geo.get("regionName"),
        "city": geo.get("city"),
        "isp": geo.get("isp"),
        "user_agent": request.headers.get("User-Agent", ""),
        "browser": f"{ua.browser.family} {ua.browser.version_string}",
        "device": ua.device.family,
        "os": ua.os.family
    })

@ip_bp.route("/get-data", methods=["POST"])
@bp_error_logger(logger=LOG.IP_BP ,return_template='error.html')
@meet_vendor_requirements
@session_set
def fetch_data():

    ip_addr = request.headers.get('X-Real-IP')
    geo_info = get_geo_info(ip_addr)

    user_agent = request.headers.get('User-Agent', '')
    ua_info = parse_user_agent(user_agent)
    LOG.IP_BP.info("-"*50)
    LOG.IP_BP.info(f"Geo data: {geo_info}")
    LOG.IP_BP.info(f"User-Agent data: {ua_info}")

    user_data = ClientAccessManager.get_recent(limit=50)
    return jsonify({"message": "success", "data": user_data}), 200

@ip_bp.route('/update', methods=['POST'])
@bp_error_logger(logger=LOG.IP_BP,status_code=500)
@session_set
def update():
    data = request.get_json()
    ip_addr = data.get('ip') if data else None
    if not ip_addr:
        ip_addr = request.headers['X-Real-IP']

    geo = get_geo_info(ip_addr)
    LOG.IP_BP.info(f"Geo data: {geo}")

    ip_exists = ClientAccessManager.get_by_ip(ip_addr) !=None
    if ip_exists:
        return jsonify({"message":"failed to update ip-exists" ,"data":"None"})

    log_geo_data(ip_addr)
    return jsonify({"message": "success" ,"data":geo}), 200


@ip_bp.route('/delete-ip', methods=['POST'])
@bp_error_logger(logger=LOG.IP_BP ,status_code=500)
@meet_vendor_requirements
@session_set
def delete_ip():
    data = request.get_json()
    ip_id = data.get('id')
    if not ip_id:
        return jsonify({"message": "IP ID required"}), 400
    
    ClientAccessManager.delete_by_id(ip_id)
    
    return jsonify({"message": "success"}), 200


@ip_bp.route("/")
@ip_bp.route("/home")
@bp_error_logger(logger=LOG.IP_BP ,return_template='error.html')
@meet_vendor_requirements
@session_set
def home():
    return render_template("ips/index.html")
