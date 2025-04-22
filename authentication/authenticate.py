import json
import requests
import base64
from datetime import datetime



class Auth:
    def __init__(self):
        self.app_key = ""
        self.app_secret = ""
        self.callbackUrl=""
        self.address = '/Schwab/experimental_app/authentication/tokens/tokens.json'
        self.address_time = '/Schwab/experimental_app/authentication/tokens/token_time.txt'
  
    def get_access_token(self):
        token_dict = json.load(open(self.address, 'r'))  
        refresh_time = token_dict.get('refresh_time')
        if "access_time" in token_dict and (datetime.now()-datetime.strptime(token_dict.get('access_time'), "%Y-%m-%d %H:%M:%S")).total_seconds()>1200:
            encoded_val=base64.b64encode(bytes(f"{self.app_key}:{self.app_secret}", "utf-8")).decode("utf-8")
            refresh_token=token_dict['refresh_token']
            headers = {'Authorization': f'Basic {encoded_val}',
                    'Content-Type': 'application/x-www-form-urlencoded'}
            data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}  # refreshes the access token
            response=requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
            c=0
            while not response.ok and c<=50:
                response=requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data);c+=1
            if not response.ok: print(f"Issue in getting access token response. Count in {c}", flush = True); return 
            token_dict=response.json()
            flag, c = not token_dict.get("access_token", None), 0
            while flag and c<=50:
                response=requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data);c+=1
                if response.ok: 
                    token_dict = response.json()
                    flag = not token_dict.get("access_token", None)
                else:
                    flag = True
            if flag and c>50: print(f"Issue in getting access token_dict. Count in {c}", flush = True); return 
            access_token = token_dict.get('access_token')
            token_dict.update({'access_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            token_dict.update({'refresh_time':refresh_time})
            with open(self.address, 'w') as json_file:
                json.dump(token_dict, json_file, indent=4)
        else:
            access_token = token_dict.get('access_token')
        return access_token
    
    def get_refresh_token(self):
        authUrl = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={self.app_key}&redirect_uri={self.callbackUrl}'
        print(f"Click to authenticate: {authUrl}")
        print("Once you are done with the website, pass the redirect url on the box on top (in VSCode)")
        responseURL = input("Pass the redirect URL here:")
        encoded_val=base64.b64encode(bytes(f"{self.app_key}:{self.app_secret}", "utf-8")).decode("utf-8")
        code = f"{responseURL[responseURL.index('code=') + 5:responseURL.index('%40')]}@"
        headers = {'Authorization': f'Basic {encoded_val}',
                'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': self.callbackUrl,'client_id':self.app_key,'client_secret': self.app_secret}
        response=requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
        token_dict=response.json()
        token_dict.update({'access_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        token_dict.update({'refresh_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        with open(self.address, 'w') as json_file:
            json.dump(token_dict, json_file, indent=4)
        print(token_dict)

    def sanity_check(self):
        "Some sanity check will be written"
        pass
        
            
                


