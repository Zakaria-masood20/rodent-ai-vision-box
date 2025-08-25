"""
License Key Management System for Commercial Deployment
Handles license validation, customer identification, and feature enablement
"""

import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import requests
from pathlib import Path
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class LicenseManager:
    """Manages license keys and customer configurations for commercial deployment"""
    
    LICENSE_FORMAT = re.compile(r'^LK-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$')
    LICENSE_SERVER = "https://license.rodent-ai.com/api/v1"  # Update with actual server
    
    def __init__(self, config_path: str = "config/license.json"):
        self.config_path = Path(config_path)
        self.license_data = self._load_license()
        self.encryption_key = self._get_encryption_key()
        
    def _get_encryption_key(self) -> bytes:
        """Generate encryption key from hardware ID"""
        hardware_id = self._get_hardware_id()
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'rodent-ai-2025',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(hardware_id.encode()))
        return key
    
    def _get_hardware_id(self) -> str:
        """Get unique hardware identifier"""
        try:
            # Try to get MAC address
            with open('/sys/class/net/eth0/address', 'r') as f:
                return f.read().strip()
        except:
            # Fallback to CPU serial on Raspberry Pi
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('Serial'):
                            return line.split(':')[1].strip()
            except:
                return "default-hardware-id"
    
    def _load_license(self) -> Dict:
        """Load license configuration from encrypted file"""
        if not self.config_path.exists():
            return {}
        
        try:
            with open(self.config_path, 'r') as f:
                encrypted_data = f.read()
                fernet = Fernet(self.encryption_key)
                decrypted = fernet.decrypt(encrypted_data.encode())
                return json.loads(decrypted)
        except:
            return {}
    
    def _save_license(self):
        """Save license configuration to encrypted file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(json.dumps(self.license_data).encode())
        
        with open(self.config_path, 'w') as f:
            f.write(encrypted.decode())
    
    def validate_license_format(self, license_key: str) -> bool:
        """Check if license key matches expected format"""
        return bool(self.LICENSE_FORMAT.match(license_key))
    
    def validate_license_online(self, license_key: str) -> Tuple[bool, Dict]:
        """Validate license with central server"""
        if not self.validate_license_format(license_key):
            return False, {"error": "Invalid license format"}
        
        try:
            response = requests.post(
                f"{self.LICENSE_SERVER}/validate",
                json={
                    'license_key': license_key,
                    'hardware_id': self._get_hardware_id(),
                    'version': '1.0.0'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    # Cache license data
                    self.license_data = {
                        'license_key': license_key,
                        'customer_id': data.get('customer_id'),
                        'customer_name': data.get('customer_name'),
                        'subscription_tier': data.get('tier', 'basic'),
                        'features': data.get('features', {}),
                        'sms_quota': data.get('sms_quota', 100),
                        'expiry_date': data.get('expiry_date'),
                        'last_validated': datetime.now().isoformat()
                    }
                    self._save_license()
                    return True, self.license_data
                else:
                    return False, {"error": data.get('message', 'Invalid license')}
            else:
                return False, {"error": f"Server error: {response.status_code}"}
                
        except requests.RequestException as e:
            # Fallback to offline validation if cached
            if self.license_data.get('license_key') == license_key:
                return True, self.license_data
            return False, {"error": f"Cannot reach license server: {str(e)}"}
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """Activate a new license key"""
        valid, data = self.validate_license_online(license_key)
        
        if valid:
            # Register device with server
            try:
                response = requests.post(
                    f"{self.LICENSE_SERVER}/activate",
                    json={
                        'license_key': license_key,
                        'hardware_id': self._get_hardware_id(),
                        'activation_date': datetime.now().isoformat()
                    }
                )
                
                if response.status_code == 200:
                    return True, f"License activated for {data.get('customer_name')}"
                else:
                    return False, "Activation failed on server"
                    
            except requests.RequestException:
                # Allow offline activation
                return True, "License activated (offline mode)"
        else:
            return False, data.get('error', 'Invalid license')
    
    def check_feature(self, feature: str) -> bool:
        """Check if a feature is enabled for current license"""
        if not self.license_data:
            return False
            
        # Check if license is expired
        if self.is_expired():
            return False
            
        features = self.license_data.get('features', {})
        tier = self.license_data.get('subscription_tier', 'basic')
        
        # Tier-based features
        tier_features = {
            'basic': ['sms_alerts', 'basic_detection'],
            'professional': ['sms_alerts', 'basic_detection', 'multi_camera', 'api_access'],
            'enterprise': ['sms_alerts', 'basic_detection', 'multi_camera', 'api_access', 
                         'white_label', 'unlimited_sms', 'custom_model']
        }
        
        return feature in tier_features.get(tier, []) or features.get(feature, False)
    
    def get_sms_quota(self) -> Dict:
        """Get SMS quota information"""
        if not self.license_data:
            return {'monthly_limit': 0, 'remaining': 0}
            
        return {
            'monthly_limit': self.license_data.get('sms_quota', 100),
            'remaining': self._get_remaining_sms(),
            'reset_date': self._get_quota_reset_date()
        }
    
    def _get_remaining_sms(self) -> int:
        """Calculate remaining SMS for current month"""
        # This would connect to usage tracking
        # For now, return quota minus estimated usage
        quota = self.license_data.get('sms_quota', 100)
        # TODO: Implement actual usage tracking
        return quota
    
    def _get_quota_reset_date(self) -> str:
        """Get next quota reset date"""
        now = datetime.now()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        return next_month.isoformat()
    
    def is_expired(self) -> bool:
        """Check if license is expired"""
        if not self.license_data:
            return True
            
        expiry = self.license_data.get('expiry_date')
        if not expiry:
            return False  # No expiry means perpetual license
            
        try:
            expiry_date = datetime.fromisoformat(expiry)
            return datetime.now() > expiry_date
        except:
            return False
    
    def get_customer_info(self) -> Dict:
        """Get customer information"""
        if not self.license_data:
            return {}
            
        return {
            'customer_id': self.license_data.get('customer_id'),
            'customer_name': self.license_data.get('customer_name'),
            'subscription_tier': self.license_data.get('subscription_tier'),
            'license_status': 'expired' if self.is_expired() else 'active'
        }
    
    def report_usage(self, metric: str, value: int):
        """Report usage metrics to central server"""
        if not self.license_data:
            return
            
        try:
            requests.post(
                f"{self.LICENSE_SERVER}/usage",
                json={
                    'customer_id': self.license_data.get('customer_id'),
                    'license_key': self.license_data.get('license_key'),
                    'metric': metric,
                    'value': value,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=5
            )
        except:
            # Silent fail for usage reporting
            pass


class SMSQuotaManager:
    """Manages SMS quotas and usage tracking"""
    
    def __init__(self, license_manager: LicenseManager):
        self.license_manager = license_manager
        self.usage_file = Path("data/sms_usage.json")
        self.usage_data = self._load_usage()
    
    def _load_usage(self) -> Dict:
        """Load SMS usage data"""
        if not self.usage_file.exists():
            return {'monthly': {}, 'daily': {}, 'total': 0}
            
        try:
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        except:
            return {'monthly': {}, 'daily': {}, 'total': 0}
    
    def _save_usage(self):
        """Save SMS usage data"""
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_data, f)
    
    def can_send_sms(self) -> Tuple[bool, str]:
        """Check if SMS can be sent based on quota"""
        quota_info = self.license_manager.get_sms_quota()
        
        # Check monthly quota
        month_key = datetime.now().strftime("%Y-%m")
        monthly_usage = self.usage_data['monthly'].get(month_key, 0)
        
        if monthly_usage >= quota_info['monthly_limit']:
            return False, f"Monthly SMS quota exceeded ({quota_info['monthly_limit']} messages)"
        
        # Check daily limit (10% of monthly)
        day_key = datetime.now().strftime("%Y-%m-%d")
        daily_limit = max(1, quota_info['monthly_limit'] // 10)
        daily_usage = self.usage_data['daily'].get(day_key, 0)
        
        if daily_usage >= daily_limit:
            return False, f"Daily SMS limit reached ({daily_limit} messages)"
        
        return True, "OK"
    
    def record_sms_sent(self):
        """Record that an SMS was sent"""
        month_key = datetime.now().strftime("%Y-%m")
        day_key = datetime.now().strftime("%Y-%m-%d")
        
        # Update monthly usage
        if month_key not in self.usage_data['monthly']:
            self.usage_data['monthly'] = {month_key: 0}
        self.usage_data['monthly'][month_key] += 1
        
        # Update daily usage
        if day_key not in self.usage_data['daily']:
            self.usage_data['daily'] = {day_key: 0}
        self.usage_data['daily'][day_key] += 1
        
        # Update total
        self.usage_data['total'] += 1
        
        self._save_usage()
        
        # Report to license server
        self.license_manager.report_usage('sms_sent', 1)
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        quota_info = self.license_manager.get_sms_quota()
        month_key = datetime.now().strftime("%Y-%m")
        day_key = datetime.now().strftime("%Y-%m-%d")
        
        return {
            'monthly': {
                'used': self.usage_data['monthly'].get(month_key, 0),
                'limit': quota_info['monthly_limit'],
                'remaining': quota_info['remaining']
            },
            'daily': {
                'used': self.usage_data['daily'].get(day_key, 0),
                'limit': max(1, quota_info['monthly_limit'] // 10)
            },
            'total_sent': self.usage_data['total'],
            'reset_date': quota_info['reset_date']
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize license manager
    lm = LicenseManager()
    
    # Test license validation
    test_key = "LK-TEST-1234-ABCD"
    valid, info = lm.validate_license_online(test_key)
    print(f"License valid: {valid}")
    print(f"Info: {info}")
    
    # Check features
    print(f"SMS Alerts enabled: {lm.check_feature('sms_alerts')}")
    print(f"Multi-camera enabled: {lm.check_feature('multi_camera')}")
    
    # Check SMS quota
    quota = lm.get_sms_quota()
    print(f"SMS Quota: {quota}")
    
    # Test SMS quota manager
    sqm = SMSQuotaManager(lm)
    can_send, message = sqm.can_send_sms()
    print(f"Can send SMS: {can_send} - {message}")
    
    # Get usage stats
    stats = sqm.get_usage_stats()
    print(f"Usage stats: {stats}")