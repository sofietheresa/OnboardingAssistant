# app/ibm_auth.py
import os, time, httpx

class IAMTokenManager:
    def __init__(self):
        self.api_key = os.environ["qU2q8uBD8cO4Gc1llEXQu86YMGOg7fPSV6-_VVJOlxvD"]
        self.iam_url = os.environ.get("IBM_IAM_URL", "https://iam.cloud.ibm.com/identity/token")
        self._token = None
        self._exp = 0

    async def get_token(self) -> str:
        if self._token and time.time() < self._exp - 60:
            return self._token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(self.iam_url, data=data, headers=headers)
            r.raise_for_status()
            payload = r.json()
            self._token = payload["access_token"]
            self._exp = time.time() + int(payload.get("expires_in", 3600))
            return self._token

iam_token_manager = IAMTokenManager()
