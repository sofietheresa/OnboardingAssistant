# app/security.py
import re
import base64
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Validates various security-related inputs"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate WatsonX API key format"""
        if not api_key or len(api_key) < 20:
            return False
        
        # Basic format check - should be alphanumeric with some special chars
        if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
            return False
            
        return True
    
    @staticmethod
    def validate_project_id(project_id: str) -> bool:
        """Validate WatsonX project ID format"""
        if not project_id:
            return False
        
        # Project ID should be UUID-like format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, project_id, re.IGNORECASE))
    
    @staticmethod
    def validate_database_url(database_url: str) -> bool:
        """Validate database URL format"""
        if not database_url:
            return False
        
        # Basic PostgreSQL URL format check
        postgres_pattern = r'^postgresql://[^:]+:[^@]+@[^:]+:\d+/.+$'
        return bool(re.match(postgres_pattern, database_url))
    
    @staticmethod
    def validate_ssl_certificate(cert: str) -> bool:
        """Validate SSL certificate format"""
        if not cert:
            return False
        
        try:
            # Try to decode base64
            decoded = base64.b64decode(cert)
            # Basic check if it looks like a certificate
            return b'-----BEGIN CERTIFICATE-----' in decoded
        except Exception:
            return False

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data for logging"""
    if not data or len(data) <= visible_chars:
        return '*' * len(data) if data else ''
    
    return data[:visible_chars] + '*' * (len(data) - visible_chars)

class SecretManager:
    """Simple secret management for sensitive data"""
    
    def __init__(self, master_key: Optional[str] = None):
        if master_key:
            # Use provided key
            key = hashlib.sha256(master_key.encode()).digest()
        else:
            # Use default key (not recommended for production)
            key = hashlib.sha256(b'default_boardy_key').digest()
        
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data

class SecurityLogger:
    """Enhanced logging with security considerations"""
    
    @staticmethod
    def log_api_call(endpoint: str, method: str, status_code: int, user_agent: Optional[str] = None):
        """Log API calls with security context"""
        logger.info(f"API Call: {method} {endpoint} -> {status_code}")
        if user_agent:
            logger.debug(f"User-Agent: {user_agent}")
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        logger.warning(f"Security Event: {event_type} - {details}")
    
    @staticmethod
    def log_authentication_attempt(success: bool, user_id: Optional[str] = None):
        """Log authentication attempts"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"Authentication {status}" + (f" for user {user_id}" if user_id else ""))
