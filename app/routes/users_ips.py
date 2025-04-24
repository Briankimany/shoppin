
from flask import request ,render_template ,jsonify ,Blueprint
from user_agents import parse as parse_user_agent
import requests

from app.data_manager.client_access_manager import ClientAccessManager

from config.config import JSONConfig
from app.routes.logger import LOG ,bp_error_logger
from app.routes.routes_utils import session_set ,meet_vendor_requirements ,get_user_ip

from curl_cffi import requests
from bs4 import BeautifulSoup as Soup

config = JSONConfig('config.json')

ip_bp = Blueprint('ips', __name__,url_prefix='/ips')


def get_ip_data(ip_addr):
    """
    Using whatsmyipaddress 
    """
    url = f"https://whatismyipaddress.com/ip/{ip_addr}"

    try:
        response = requests.get(url ,impersonate="chrome")
    except Exception as e:
        LOG.IP_BP.error("[IP-WHATS] Could not fetch ip informaiton ")
        LOG.IP_BP.error(f"[IP-WHATS] e=({e}")
        return {}
    
    data = Soup(response.text, 'html.parser')
   
    target_div = data.select_one(
        "#fl-post-1165 > div > div > div.fl-row.fl-row-fixed-width.fl-row-bg-none.fl-node-5d9c0c38837c0 > div > div.fl-row-content.fl-row-fixed-width.fl-node-content > div > div.fl-col.fl-node-5d9c0c3888731 > div > div.fl-module.fl-module-wipa-static-html.fl-node-5d9e84c8187fe > div > div > div > div.inner > div.left"
    )

    if target_div:

        LOG.IP_BP.debug("[IP-WHATS] Retrieved div for parsing")

        geo_data = {}
        for p in target_div.select('p.information'):
            try:
                spans = p.find_all('span')
                if len(spans) == 2:
                    key = spans[0].text.strip().rstrip(':')
                    value = spans[1].text.strip()
                    geo_data[key] = value
            except Exception as e:
                pass
        data = {
        "country": geo_data.get("Country"),
        "region": geo_data.get("State/Region"),
        "city": geo_data.get("City"),
        "isp": geo_data.get("ISP")}
        
        LOG.IP_BP.debug(f'[IP-WHATS] Retrived data = {geo_data}')
        return {k:v for k,v in data.items() if v}
    
    else:
        LOG.IP_BP.debug(f"[IP-ERROR] Could not extract info for {ip_addr}")
        return {}
    


def get_geo_info(ip_address) -> dict:
    try:
        response = requests.get(config.ip_url.format(ip_address))
        return response.json()
    except Exception as e:
        LOG.IP_BP.critical(f"Could not fetch ip data ,ip=({ip_address})" )
        return {}

def log_geo_data(ip_addr):

    LOG.IP_BP.debug("-"*50)
    LOG.IP_BP.info(f"[IP-UPDATE] Recording {ip_addr}")

    ua = parse_user_agent(request.headers.get("User-Agent", ""))
    LOG.IP_BP.info(f"User-Agent data: {ua}")

    geo = get_geo_info(ip_addr)
    LOG.IP_BP.debug(f"[API-GEO] IP: {ip_addr} → {geo}")

    geo.update(get_ip_data(ip_addr))
    LOG.IP_BP.info(f"[GEO] IP: {ip_addr} → {geo}")
    

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
        "os": ua.os.family,
        "consent_given":True
    })

    LOG.IP_BP.debug("-"*50)

    return geo

@ip_bp.route("/get-data", methods=["POST"])
@bp_error_logger(logger=LOG.IP_BP ,return_template='error.html')
@meet_vendor_requirements
@session_set
def fetch_data():

    user_data = ClientAccessManager.get_recent(limit=50)
    return jsonify({"message": "success", "data": user_data}), 200

@ip_bp.route('/update', methods=['POST'])
@bp_error_logger(logger=LOG.IP_BP,status_code=500)
@session_set
def update():
    data = request.get_json()
    ip_addr = data.get('ip') if data else None

    if not ip_addr:
        ip_addr =get_user_ip()

    ip_exists = ClientAccessManager.get_by_ip(ip_addr) !=None
    if ip_exists:
        LOG.IP_BP.info(f"[IP-DUP] Ip already recorded {ip_addr}")
        return jsonify({"message":"failed to update ip-exists" ,"data":None})
    
    geo = log_geo_data(ip_addr)
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
