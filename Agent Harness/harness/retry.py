import logging
from config import MAX_RETRIES

logger = logging.getLogger(__name__)

class RetryManager:
    def classify_error(self, error: Exception) -> str:
        error_msg = str(error).lower()
        if "timeout" in error_msg:
            return "TIMEOUT"
        elif "element not found" in error_msg or "waiting for selector" in error_msg or "strict mode violation" in error_msg:
            return "RECOVERABLE"
        elif "policy_violation" in error_msg:
             return "POLICY_VIOLATION"
        elif "requires_approval" in error_msg:
             return "USER_ACTION_REQUIRED"
        
        return "UNKNOWN"

    def can_retry(self, error_type: str, current_retry: int) -> bool:
        if error_type in ["POLICY_VIOLATION", "USER_ACTION_REQUIRED"]:
            return False
        
        if current_retry >= MAX_RETRIES:
            return False
            
        return True
