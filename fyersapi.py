import requests,time, hmac, base64, struct, os
from fyers_apiv3 import fyersModel
from urllib.parse import urlparse, parse_qs
import json

class FyersApp:
    def __init__(self, config_path = "config.json") -> None:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(config['username'])
        self.__username = config["username"]
        self.__totp_key = config["totp_key"]
        self.__pin = config["pin"]
        self.__client_id = config["client_id"]
        self.__secret_key = config["secret_key"]
        self.__redirect_uri = config["redirect_uri"]
        self.__access_token = None

    def enable_app(self):
        appSession = fyersModel.SessionModel(
            client_id = self.__client_id, 
            redirect_uri = self.__redirect_uri, 
            response_type= 'code', 
            state= 'state', 
            secret_key= self.__secret_key, 
            grant_type= 'authorization_code'
            )
        return appSession.generate_authcode()
    
    def __totp(self, key, time_step=30, digits=6, digest="sha1"):
        key = base64.b32decode(key.upper() + "=" * ((8 - len(key)) % 8))
        counter = struct.pack(">Q", int(time.time() / time_step))
        mac = hmac.new(key, counter, digest).digest()
        offset = mac[-1] & 0x0F
        binary = struct.unpack(">L", mac[offset : offset + 4])[0] & 0x7FFFFFFF
        return str(binary)[-digits:].zfill(digits)
    
    def generate_token(self, refresh = False):
        if self.__access_token == None and refresh != False:
            return
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        }

        s = requests.Session()
        s.headers.update(headers)

        data1 = f'{{"fy_id":"{base64.b64encode(f"{self.__username}".encode()).decode()}","app_id":"2"}}'
        r1 = s.post("https://api-t2.fyers.in/vagator/v2/send_login_otp_v2", data=data1)

        request_key = r1.json()["request_key"]
        data2 = f'{{"request_key":"{request_key}","otp":{self.__totp(self.__totp_key)}}}'
        r2 = s.post("https://api-t2.fyers.in/vagator/v2/verify_otp", data=data2)
        assert r2.status_code == 200, f"Error in r2:\n {r2.text}"

        request_key = r2.json()["request_key"]
        data3 = f'{{"request_key":"{request_key}","identity_type":"pin","identifier":"{base64.b64encode(f"{self.__pin}".encode()).decode()}"}}'
        r3 = s.post("https://api-t2.fyers.in/vagator/v2/verify_pin_v2", data=data3)
        assert r3.status_code == 200, f"Error in r3:\n {r3.json()}"

        headers = {"authorization": f"Bearer {r3.json()['data']['access_token']}", "content-type": "application/json; charset=UTF-8"}
        data4 = f'{{"fyers_id":"{self.__username}","app_id":"{self.__client_id[:-4]}","redirect_uri":"{self.__redirect_uri}","appType":"100","code_challenge":"","state":"abcdefg","scope":"","nonce":"","response_type":"code","create_cookie":true}}'
        r4 = s.post("https://api.fyers.in/api/v2/token", headers=headers, data=data4)
        assert r4.status_code == 308, f"Error in r4:\n {r4.json()}"

        parsed = urlparse(r4.json()["Url"])
        auth_code = parse_qs(parsed.query)["auth_code"][0]

        session = fyersModel.SessionModel(
            client_id= self.__client_id, 
            secret_key= self.__secret_key, 
            redirect_uri= self.__redirect_uri, 
            response_type="code", 
            grant_type="authorization_code"
            )
        session.set_token(auth_code)
        response = session.generate_token()
        self.__access_token = response["access_token"]
        return self.__access_token

    def get_profile(self):
        fyers = fyersModel.FyersModel(client_id=self.__client_id, token=self.__access_token, log_path=os.getcwd())
        return fyers.get_profile()

if __name__ == '__main__':
    app = FyersApp()
    # print(app.enable_app())
    accessToken = app.generate_token()
    from pprint import pprint
    pprint(app.get_profile())
    #save to txt file
    with open("client_id.txt",'w') as file:
        file.write(app._FyersApp__client_id)

    with open("access_token.txt",'w') as file:
        file.write(app._FyersApp__access_token)