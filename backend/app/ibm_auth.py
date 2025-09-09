# app/ibm_auth.py
import os
import asyncio
from typing import Optional
import httpx
from datetime import datetime, timedelta

class IAMTokenManager:
    def __init__(self):
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self._lock = asyncio.Lock()
        
        if not self.api_key:
            raise ValueError("WATSONX_API_KEY environment variable is required")

    async def get_token(self) -> str:
        """Get a valid IAM token, refreshing if necessary"""
        async with self._lock:
            if self._is_token_valid():
                return self.token
            
            await self._refresh_token()
            return self.token

    def _is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        if not self.token or not self.token_expires_at:
            return False
        
        # Refresh token 5 minutes before expiry
        buffer_time = timedelta(minutes=5)
        return datetime.now() < (self.token_expires_at - buffer_time)

    async def _refresh_token(self):
        """Refresh the IAM token"""
        try:
            url = "https://iam.cloud.ibm.com/identity/token"
            data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data, headers=headers)
                response.raise_for_status()
                
                token_data = response.json()
                self.token = token_data["access_token"]
                
                # Calculate expiry time (default to 1 hour if not provided)
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
        except Exception as e:
            raise RuntimeError(f"Failed to refresh IAM token: {e}")

# Global instance - lazy initialization
iam_token_manager: Optional[IAMTokenManager] = None

def get_iam_token_manager() -> IAMTokenManager:
    """Get the global IAM token manager instance, creating it if necessary"""
    global iam_token_manager
    if iam_token_manager is None:
        iam_token_manager = IAMTokenManager()
    return iam_token_manager
