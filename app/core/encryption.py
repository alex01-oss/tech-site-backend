import base64
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
import logging

from app.core.settings import settings


logger = logging.getLogger(__name__)

class EncryptionService:
    def __init__(self):
        key = settings.ENCRYPTION_KEY
        
        if not key:
            raise ValueError("ENCRYPTION_KEY not found in settings")
        
        try:
            if not isinstance(key, str):
                raise ValueError("ENCRYPTION_KEY must be a string")

            if not self._is_valid_fernet_key(key):
                raise ValueError("ENCRYPTION_KEY must be 32 url-safe base64-encoded bytes")
            
            self.fernet = Fernet(key)
            self._test_encryption()
            
        except Exception as e:
            logger.critical(f"Failed to initialize encryption service: {e}")
            raise ValueError(f"Invalid encryption key: {e}")
    
    def _is_valid_fernet_key(self, key: str) -> bool:
        try:
            decoded = base64.urlsafe_b64decode(key)
            return len(decoded) == 32
        except:
            return False
    
    def _test_encryption(self):
        test_data = "test_encryption"
        try:
            encrypted = self.fernet.encrypt(test_data.encode())
            decrypted = self.fernet.decrypt(encrypted).decode()
            if decrypted != test_data:
                raise ValueError("Encryption test failed")
        except Exception as e:
            raise ValueError(f"Encryption test failed: {e}")
    
    def encrypt_data(self, data: str) -> str:
        if not data:
            return ''
        
        try:
            return self.fernet.encrypt(data.encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed for data length {len(data)}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Encryption failed"
            )

    def decrypt_data(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return ''
        
        try:
            return self.fernet.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or corrupted data")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data corruption detected"
            )
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Decryption failed"
            )

def create_encryption_service() -> EncryptionService:
    try:
        return EncryptionService()
    except Exception as e:
        logger.critical(f"Failed to create encryption service: {e}")
        raise

encryption_service = create_encryption_service()
