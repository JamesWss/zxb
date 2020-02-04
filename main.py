from io import BytesIO
import rsa
from config import URL, USER, VERIFY, PWD, PROXY_NAME, PROXY_PORT
import requests
from lxml import etree
from mitmproxy import http

session = requests.Session()
session.headers[
    "User-Agent"] = headers = "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Mobile Safari/537.36 Edg/85.0.564.41"

rsp = session.get(f"{URL}/por/login_auth.csp?apiversion=1", verify=VERIFY)
xml = etree.parse(BytesIO(rsp.content))

rsa_key = xml.xpath("/Auth/RSA_ENCRYPT_KEY/text()")[0]
rand_code = xml.xpath("/Auth/CSRF_RAND_CODE/text()")[0]

pub_key = rsa.PublicKey(int(rsa_key, 16), 65537)

encrypted_pwd = rsa.encrypt(f"{PWD}_{rand_code}".encode("utf-8"), pub_key).hex()

rsp = session.post(f"{URL}/por/login_psw.csp?anti_replay=1&encrypt=1&apiversion=1", data={
    'mitm_result': '',
    'svpn_req_randcode': rand_code,
    'svpn_name': USER,
    'svpn_password': encrypted_pwd,
    'svpn_rand_code': ''
}, verify=False)
print(rsp.text)
print(session.cookies)


def request(flow: http.HTTPFlow):
    req = flow.request
    if PROXY_NAME not in req.host:
        req.host = req.host.replace(".", "-") + "." + PROXY_NAME
        req.port = PROXY_PORT
        req.cookies.add("TWFID", session.cookies.get("TWFID"))
